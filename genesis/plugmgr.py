"""
Tools for manipulating plugins and repository
"""

__all__ = [
    'BaseRequirementError',
    'PlatformRequirementError',
    'PluginRequirementError',
    'ModuleRequirementError',
    'SoftwareRequirementError',
    'PluginLoader',
    'RepositoryManager',
    'PluginInfo',
]

import os
import imp
import json
import shutil
import sys
import tarfile
import traceback
import weakref
import urllib2

from genesis.api import *
from genesis.com import *
from genesis.utils import detect_platform, shell, shell_cs, shell_status
import genesis

RETRY_LIMIT = 10


class BaseRequirementError(Exception):
    """
    Basic exception that means a plugin wasn't loaded due to unmet
    dependencies
    """


class PlatformRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    unsupported platform
    """

    def __init__(self, lst):
        BaseRequirementError.__init__(self)
        self.lst = lst

    def __str__(self):
        return 'requires platforms %s' % self.lst


class GenesisVersionRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    unsupported Genesis version
    """

    def __init__(self, lst):
        BaseRequirementError.__init__(self)
        self.lst = lst

    def __str__(self):
        return 'requires %s' % self.lst


class PluginRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required plugin being unavailable
    """

    def __init__(self, dep):
        BaseRequirementError.__init__(self)
        self.name = dep['name']
        self.package = dep['package']

    def __str__(self):
        return 'requires plugin "%s"' % self.name


class ModuleRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required Python module being unavailable
    """

    def __init__(self, dep, restart):
        BaseRequirementError.__init__(self)
        self.name = dep['name'] if type(dep) == dict else dep
        self.restart = restart

    def __str__(self):
        if self.restart:
            return 'Dependency "%s" has been installed. Please reload Genesis to use this plugin.' % self.name
        else:
            return 'requires Python module "%s"' % self.name


class SoftwareRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required software being unavailable
    """

    def __init__(self, dep):
        BaseRequirementError.__init__(self)
        self.name = dep['name']
        self.pack = dep['package']
        self.bin = dep['binary']

    def __str__(self):
        return 'requires application "%s" (package: %s, executable: %s)' % (self.name, self.pack, self.bin)


class CrashedError(BaseRequirementError):
    """
    Exception that means a plugin crashed during load
    """

    def __init__(self, inner):
        BaseRequirementError.__init__(self)
        self.inner = inner

    def __str__(self):
        return 'crashed during load: %s' % self.inner


class ImSorryDave(Exception):
    """
    General exception when an attempted operation has a conflict
    """
    def __init__(self, target, depend, reason):
        self.target = target
        self.reason = reason
        self.depend = depend

    def __str__(self):
        if self.reason == 'remove':
            return ('%s can\'t be removed, as %s still depends on it. '
                'Please remove that first if you would like to remove '
                'this plugin.' % (self.target, self.depend))
        else:
            return ('%s can\'t be installed, as it depends on %s. Please '
                'install that first.' % (self.target, self.depend))


class PluginLoader:
    """
    Handles plugin loading and unloading
    """

    __classes = {}
    __plugins = {}
    __submods = {}
    __managers = []
    __observers = []
    platform = None
    log = None
    path = None

    @staticmethod
    def initialize(log, path, arch, platform):
        """
        Initializes the PluginLoader

        :param  log:        Logger
        :type   log:        :class:`logging.Logger`
        :param  path:       Path to the plugins
        :type   path:       str
        :param  platform:   System platform for plugin validation
        :type   platform:   str
        """

        PluginLoader.log = log
        PluginLoader.path = path
        PluginLoader.arch = arch
        PluginLoader.platform = platform

    @staticmethod
    def list_plugins():
        """
        Returns dict of :class:`PluginInfo` for all plugins
        """

        return PluginLoader.__plugins

    @staticmethod
    def register_mgr(mgr):
        """
        Registers an :class:`genesis.com.PluginManager` from which the unloaded
        classes will be removed when a plugin is unloaded
        """
        PluginLoader.__managers.append(mgr)

    @staticmethod
    def register_observer(mgr):
        """
        Registers an observer which will be notified when plugin set is changed.
        Observer should have a callable ``plugins_changed`` method.
        """
        PluginLoader.__observers.append(weakref.ref(mgr,
            callback=PluginLoader.__unregister_observer))

    @staticmethod
    def __unregister_observer(ref):
        PluginLoader.__observers.remove(ref)

    @staticmethod
    def notify_plugins_changed():
        """
        Notifies all observers that plugin set has changed.
        """
        for o in PluginLoader.__observers:
            if o():
                o().plugins_changed()

    @staticmethod
    def load(plugin, cat=''):
        """
        Loads given plugin
        """
        log = PluginLoader.log
        path = PluginLoader.path
        platform = PluginLoader.platform
        from genesis import generation, version

        if cat:
            cat.statusmsg('Loading plugin %s...' % plugin)
        log.debug('Loading plugin %s' % plugin)

        try:
            mod = imp.load_module(plugin, *imp.find_module(plugin, [path]))
            meta = json.load(open(os.path.join(path, plugin, 'plugin.json'), 'r'))
            log.debug('  -- version ' + meta['version'])
        except Exception, e:
            log.warn(' *** Plugin not loadable: ' + plugin)
            log.warn(str(e))
            return

        info = PluginInfo()
        try:
            d = None
            # Save info
            info.id = plugin
            info.ptype = meta['type']
            info.icon = meta['icon']
            info.services = meta['services'] if meta.has_key('services') else []
            info.name, info.version = meta['name'], meta['version']
            info.desc, info.longdesc = meta['description']['short'], meta['description']['long'] if meta['description'].has_key('long') else ''
            info.author, info.homepage, info.logo = meta['author'], meta['homepage'], meta['logo'] if meta.has_key('logo') else False
            info.app_author, info.app_homepage = meta['app_author'] if meta.has_key('app_author') else None, \
                meta['app_homepage'] if meta.has_key('app_homepage') else None
            info.cats = meta['categories']
            info.deps = []
            info.problem = None
            info.installed = True
            info.descriptor = meta

            # Add special information
            if info.ptype == 'webapp':
                info.wa_plugin, info.dpath = meta['website_plugin'], meta['download_url']
                info.dbengines = meta['database_engines'] if meta.has_key('database_engines') else []
                info.php, info.ssl = meta['uses_php'], meta['uses_ssl']
            elif info.ptype == 'database':
                info.db_plugin, info.db_task = meta['database_plugin'], meta['database_task']
                info.multiuser, info.requires_conn = meta['database_multiuser'], meta['database_requires_connection']
            info.f2b = meta['fail2ban'] if meta.has_key('fail2ban') else None
            info.f2b_name = meta['fail2ban_name'] if meta.has_key('fail2ban_name') else None
            info.f2b_icon = meta['fail2ban_icon'] if meta.has_key('fail2ban_icon') else None

            PluginLoader.__plugins[plugin] = info

            # Verify platform
            if meta['platforms'] != ['any'] and not platform in meta['platforms']:
                raise PlatformRequirementError(meta['platforms'])

            # Verify version
            if not meta.has_key('generation') or meta['generation'] != generation:
                raise GenesisVersionRequirementError('other Genesis platform generation')

            # Verify dependencies
            if meta.has_key('dependencies'):
                deps = []
                for k in meta['dependencies']:
                    if platform.lower() in k or 'any' in k:
                        deps = meta['dependencies'][k]
                        break
                info.deps = deps
                for req in deps:
                    d = PluginLoader.verify_dep(req, cat)

            PluginLoader.__classes[plugin] = []
            PluginLoader.__submods[plugin] = {}

            # Load submodules
            for submod in meta['modules']:
                try:
                    log.debug('  -> %s' % submod)
                    PluginManager.start_tracking()
                    m = imp.load_module(plugin + '.' + submod, *imp.find_module(submod, mod.__path__))
                    classes = PluginManager.stop_tracking()
                    # Record new Plugin subclasses
                    PluginLoader.__classes[plugin] += classes
                    # Store submodule
                    PluginLoader.__submods[plugin][submod] = m
                    setattr(mod, submod, m)
                except ImportError, e:
                    del mod
                    raise ModuleRequirementError(e.message.split()[-1], False)
                except Exception:
                    del mod
                    raise

            # Store the whole plugin
            setattr(genesis.plugins, plugin, mod)
            PluginLoader.notify_plugins_changed()
            if d:
                return d
        except BaseRequirementError, e:
            info.problem = e
            raise e
        except Exception, e:
            log.warn(' *** Plugin loading failed: %s' % str(e))
            print traceback.format_exc()
            PluginLoader.unload(plugin)
            info.problem = CrashedError(e)

    @staticmethod
    def load_plugins():
        """
        Loads all plugins from plugin path
        """
        log = PluginLoader.log
        path = PluginLoader.path

        plugs = [plug for plug in os.listdir(path) if not plug.startswith('.')]
        plugs = [plug[:-3] if plug.endswith('.py') else plug for plug in plugs]
        plugs = list(set(plugs)) # Leave just unique items

        queue = plugs
        retries = {}

        while len(queue) > 0:
            plugin = queue[-1]
            if not plugin in retries:
                retries[plugin] = 0

            try:
                PluginLoader.load(plugin)
                queue.remove(plugin)
            except PluginRequirementError, e:
                retries[plugin] += 1
                if retries[plugin] > RETRY_LIMIT:
                    log.error('Circular dependency between %s and %s. Aborting' % (plugin,e.name))
                    sys.exit(1)
                try:
                    queue.remove(e.package)
                    queue.append(e.package)
                    if (e.package in PluginLoader.__plugins) and (PluginLoader.__plugins[e.package].problem is not None):
                        raise e
                except:
                    log.warn('Plugin %s requires plugin %s, which is not available.' % (plugin,e.name))
                    queue.remove(plugin)
            except BaseRequirementError, e:
                log.warn('Plugin %s %s' % (plugin,str(e)))
                PluginLoader.unload(plugin)
                queue.remove(plugin)
            except Exception:
                PluginLoader.unload(plugin)
                queue.remove(plugin)
        log.info('Plugins loaded.')

    @staticmethod
    def unload(plugin):
        """
        Unloads given plugin
        """
        PluginLoader.log.info('Unloading plugin %s'%plugin)
        if plugin in PluginLoader.__classes:
            for cls in PluginLoader.__classes[plugin]:
                for m in PluginLoader.__managers:
                    i = m.instance_get(cls)
                    if i is not None:
                        i.unload()
                PluginManager.class_unregister(cls)
        if plugin in PluginLoader.__plugins:
            del PluginLoader.__plugins[plugin]
        if plugin in PluginLoader.__submods:
            del PluginLoader.__submods[plugin]
        if plugin in PluginLoader.__classes:
            del PluginLoader.__classes[plugin]
        PluginLoader.notify_plugins_changed()

    @staticmethod
    def verify_dep(dep, cat=''):
        """
        Verifies that given plugin dependency is satisfied.
        """
        platform = PluginLoader.platform
        log = PluginLoader.log

        if dep['type'] == 'app':
            if ((dep['binary'] and shell_status('which '+dep['binary']) != 0) \
            or not dep['binary']) and shell_status('pacman -Q '+dep['package']) != 0:
                if platform == 'arch' or platform == 'arkos':
                    if cat:
                        cat.statusmsg('Installing dependency %s...' % dep['name'])
                    log.warn('Missing %s, which is required by a plugin. Attempting to install...' % dep['name'])
                    s = shell_cs('pacman -Sy --noconfirm --needed '+dep['package'], stderr=True)
                    if s[0] != 0:
                        log.error('Failed to install %s - %s' % (dep['name'], str(s[1])))
                        raise SoftwareRequirementError(dep)
                    if dep['binary']:
                        shell('systemctl enable '+dep['binary'])
                elif platform == 'debian':
                    try:
                        shell('apt-get -y --force-yes install '+dep['package'])
                    except:
                        raise SoftwareRequirementError(dep)
                elif platform == 'gentoo':
                    try:
                        shell('emerge '+dep['package'])
                    except:
                        raise SoftwareRequirementError(dep)
                elif platform == 'freebsd':
                    try:
                        shell('portupgrade -R '+dep['package'])
                    except:
                        raise SoftwareRequirementError(dep)
                elif platform == 'centos' or platform == 'fedora':
                    try:
                        shell('yum -y install  '+dep['package'])
                    except:
                        raise SoftwareRequirementError(dep)
                else:
                    raise SoftwareRequirementError(dep)
        if dep['type'] == 'plugin':
            if not dep['package'] in PluginLoader.list_plugins() or \
                    PluginLoader.__plugins[dep['package']].problem:
                raise PluginRequirementError(dep)
        if dep['type'] == 'module':
            if dep.has_key('binary') and dep['binary']:
                try:
                    exec('import %s'%dep['binary'])
                except:
                    # Let's try to install it anyway
                    s = shell_cs('pip%s install %s' % ('2' if platform in ['arkos', 'arch'] else '', dep['package']))
                    if s[0] != 0:
                        raise ModuleRequirementError(dep, False)
                    else:
                        return 'Restart Genesis for changes to take effect.'
                        raise ModuleRequirementError(dep, False)
            else:
                p = False
                s = shell('pip%s freeze'%'2' if platform in ['arkos', 'arch'] else '')
                for x in s.split('\n'):
                    if dep['package'].lower() in x.split('==')[0].lower():
                        p = True
                if not p:
                    shell('pip%s install %s' % ('2' if platform in ['arkos', 'arch'] else '', dep['package']))
                    raise ModuleRequirementError(dep, True)

    @staticmethod
    def get_plugin_path(app, id):
        """
        Returns path for plugin's files. Parameters: :class:`genesis.core.Application`, ``str``
        """
        if id in PluginLoader.list_plugins():
            return app.config.get('genesis', 'plugins')
        else:
            return os.path.join(os.path.split(__file__)[0], 'plugins') # ./plugins


class RepositoryManager:
    """
    Manages official Genesis plugin repository. ``cfg`` is :class:`genesis.config.Config`

    - ``available`` - list(:class:`PluginInfo`), plugins available in the repository
    - ``installed`` - list(:class:`PluginInfo`), plugins that are locally installed
    - ``upgradable`` - list(:class:`PluginInfo`), plugins that are locally installed
      and have other version in the repository
    """

    def __init__(self, log, cfg):
        self.config = cfg
        self.log = log
        self.server = cfg.get('genesis', 'update_server')
        self.refresh()

    def list_available(self):
        d = {}
        for x in self.available:
            d[x.id] = x
        return d

    def check_conflict(self, id, op):
        """
        Check if an operation can be performed due to dependency conflict
        """
        pdata = PluginLoader.list_plugins()
        metoo = []
        if op == 'remove':
            for i in self.installed:
                for dep in i.deps:
                    if dep['type'] == 'plugin' and dep['package'] == id:
                        metoo.append(('Remove', i))
                        metoo += self.check_conflict(i.id, 'remove')
        elif op == 'install':
            t = self.list_available()
            for i in t[id].deps:
                for dep in t[id].deps[i]:
                    if dep['type'] == 'plugin' and dep['package'] not in [x.id for x in self.installed]:
                        for x in self.available:
                            if x.id == dep['package']:
                                metoo.append(('Install', x))
                                metoo += self.check_conflict(x.id, 'install')
        return metoo

    def refresh(self):
        """
        Re-reads saved repository information and rebuilds installed/available lists
        """
        self.available = []
        self.installed = []
        self.update_installed()
        self.update_available()
        self.update_upgradable()

    def update_available(self):
        """
        Re-reads saved list of available plugins
        """
        try:
            data = json.load(open('/var/lib/genesis/plugins.list', 'r'))
        except IOError, e:
            self.log.error('Could not load plugin list file: %s' % str(e))
            data = []
        except ValueError, e:
            self.log.error('Could not parse plugin list file: %s' % str(e))
            data = []

        self.available = []
        for item in data:
            inst = False
            for i in self.installed:
                if i.id == item['id'] and i.version == item['version']:
                    inst = True
                    break
            if inst:
                continue

            i = PluginInfo()
            for k,v in item.items():
                setattr(i, k, v)
            i.installed = False
            i.problem = None
            self.available.append(i)

    def update_installed(self):
        """
        Rebuilds list of installed plugins
        """
        self.installed = sorted(PluginLoader.list_plugins().values(), key=lambda x:x.name)

    def update_upgradable(self):
        """
        Rebuilds list of upgradable plugins
        """
        upg = []
        for p in self.available:
            for g in self.installed:
                if g.id == p.id and g.version != p.version:
                    g.upgradable = p.upgradable = True
                    upg += [p]
                    break
        self.upgradable = upg

    def update_list(self, crit=False):
        """
        Downloads fresh list of plugins and rebuilds installed/available lists
        """
        from genesis import generation, version
        if not os.path.exists('/var/lib/genesis'):
            os.mkdir('/var/lib/genesis')
        try:
            req = urllib2.Request('https://%s/' % self.server)
            req.add_header('Content-type', 'application/json')
            data = urllib2.urlopen(req, json.dumps({'get': 'list', 'distro': PluginLoader.platform})).read()
            open('/var/lib/genesis/plugins.list', 'w').write(data)
        except urllib2.HTTPError, e:
            self.log.error('Application list retrieval failed with HTTP Error %s' % str(e.code))
        except urllib2.URLError, e:
            self.log.error('Application list retrieval failed - Server not found or URL malformed. Please check your Internet settings.')
        except IOError, e:
            self.log.error('Failed to write application list to disk.')
        else:
            self.update_installed()
            self.update_available()
            self.update_upgradable()

    def remove(self, id, cat=''):
        """
        Uninstalls given plugin

        :param  id:     Plugin id
        :type   id:     str
        """

        try:
            self.purge = self.config.get('genesis', 'purge')
        except:
            self.purge = '1'

        exclude = ['openssl', 'openssh', 'nginx', 'python2']

        if cat:
            cat.statusmsg('Removing plugin...')
        dir = self.config.get('genesis', 'plugins')
        shutil.rmtree(os.path.join(dir, id))

        if id in PluginLoader.list_plugins():
            depends = []
            try:
                pdata = PluginLoader.list_plugins()
                thisplugin = pdata[id].deps
                for thing in thisplugin:
                    if 'app' in thing[0]:
                        depends.append((thing, 0))
                for plugin in pdata:
                    for item in enumerate(depends):
                        if item[1][0] in pdata[plugin].deps:
                            depends[item[0]] = (depends[item[0]][0], depends[item[0]][1]+1)
                for thing in depends:
                    if thing[1] <= 1 and not thing[0][1] in exclude:
                        if cat:
                            cat.statusmsg('Removing dependency %s...' % thing[0][1])
                        shell('systemctl stop ' + thing[0][2])
                        shell('systemctl disable ' + thing[0][2])
                        shell('pacman -%s --noconfirm ' %('Rn' if self.purge is '1' else 'R') + thing[0][1])
            except KeyError:
                pass
            PluginLoader.unload(id)

        self.update_installed()
        self.update_available()

    def install(self, id, load=True, cat=''):
        """
        Installs a plugin

        :param  id:     Plugin id
        :type   id:     str
        :param  load:   True if you want Genesis to load the plugin immediately
        :type   load:   bool
        """
        from genesis import generation, version
        dir = self.config.get('genesis', 'plugins')

        if cat:
            cat.statusmsg('Downloading plugin package...')
        try:
            req = urllib2.Request('https://%s/' % self.server)
            req.add_header('Content-type', 'application/json')
            data = urllib2.urlopen(req, json.dumps({'get': 'plugin', 'id': id}))
            if data.info()['Content-type'].startswith('application/json'):
                j = json.loads(data.read())
                self.log.error('Plugin retrieval failed - %s' % str(j['info']))
                raise Exception('Plugin retrieval failed - %s' % str(j['info']))
            else:
                open('%s/plugin.tar.gz'%dir, 'w').write(data.read())
        except urllib2.HTTPError, e:
            self.log.error('Plugin retrieval failed with HTTP Error %s' % str(e.code))
            raise Exception('Plugin retrieval failed with HTTP Error %s' % str(e.code))
        except urllib2.URLError, e:
            self.log.error('Plugin retrieval failed - Server not found or URL malformed. Please check your Internet settings.')
            raise Exception('Plugin retrieval failed - Server not found or URL malformed. Please check your Internet settings.')
        else:
            #self.remove(id)
            self.install_tar(load=load, cat=cat)

    def install_stream(self, stream):
        """
        Installs a plugin from a stream containing the package

        :param  stream: Data stream
        :type   stream: file
        """
        dir = self.config.get('genesis', 'plugins')
        open('%s/plugin.tar.gz'%dir, 'w').write(stream)
        self.install_tar()

    def install_tar(self, load=True, cat=''):
        """
        Unpacks and installs a ``plugin.tar.gz`` file located in the plugins directory.

        :param  load:   True if you want Genesis to load the plugin immediately
        :type   load:   bool
        """
        dir = self.config.get('genesis', 'plugins')

        if cat:
            cat.statusmsg('Extracting plugin package...')

        t = tarfile.open(os.path.join(dir, 'plugin.tar.gz'), 'r:gz')
        id = t.getmembers()[0].name
        t.extractall(dir)
        t.close()
        os.unlink(os.path.join(dir, 'plugin.tar.gz'))

        if cat:
            cat.statusmsg('Loading plugin...')

        if load:
            PluginLoader.load(id, cat=cat)

        self.update_installed()
        self.update_available()
        self.update_upgradable()


class PluginInfo:
    """
    Container for the plugin description
    - ``upgradable`` - `bool`, if the plugin can be upgraded
    - ``problem``- :class:`Exception` which occured while loading plugin, else ``None``
    - ``deps`` - list of dependency tuples
    And other fields read by :class:`PluginLoader` from plugin's ``__init__.py``
    """

    def __init__(self):
        self.upgradable = False
        self.problem = None
        self.deps = []
