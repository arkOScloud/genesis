from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.plugmgr import PluginLoader, RepositoryManager
from genesis.utils import *


class PluginManager(CategoryPlugin, URLHandler):
    text = 'App Store'
    iconfont = 'gen-box-add'
    folder = 'top'

    def on_session_start(self):
        self._mgr = RepositoryManager(self.app.log, self.app.config)
        self._nc = apis.networkcontrol(self.app)
        self._wa = apis.webapps(self.app)
        self._info = None
        self._metoo = []

    def on_init(self):
        self._mgr.refresh()

    def get_counter(self):
        return len(self._mgr.upgradable) or None

    def get_ui(self):
        ui = self.app.inflate('plugins:main')

        inst = sorted(self._mgr.installed, key=lambda x: x.name.lower())

        for k in inst:
            row = self.app.inflate('plugins:item')
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k.desc
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.desc)
            row.find('icon').set('class', k.icon)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)
            row.append('buttons', UI.TipIcon(
                        iconfont="gen-cancel-circle",
                        text='Uninstall',
                        id='remove/'+k.id,
                        warning='Are you sure you wish to remove "%s"? Software and data associated with this application will be removed.' % k.name,
                    ))

            if k.problem:
                row.find('status').set('iconfont', 'gen-close-2 text-error')
                row.find('status').set('text', k.problem)
                row.find('icon').set('class', k.icon + ' text-error')
                row.find('name').set('class', 'text-error')
                row.find('desc').set('class', 'text-error')
                row.append('reqs', UI.IconFont(iconfont="gen-warning text-error", text=k.problem))
            else:
                row.find('status').set('iconfont', 'gen-checkmark')
                row.find('status').set('text', 'Installed and Enabled')
            ui.append('list', row)

        lst = {}
        for x in self._mgr.available:
            if x in self._mgr.upgradable:
                continue
            for y in x.categories:
                if not lst.has_key(y['primary']):
                    lst[y['primary']] = []
                lst[y['primary']].append(x)

        if self._mgr.upgradable:
            ui.append('upg', UI.Label(size=3, text="Updates Available"))
            for x in self._mgr.upgradable:
                ui.append('upg', 
                    UI.AppButton(
                        id=x.id,
                        name=x.name,
                        iconfont=x.icon,
                        version=x.version
                        )
                    )
        
        for x in lst:
            ui.append('avail', UI.Label(size=3, text=x))
            for y in sorted(lst[x], key=lambda z: z.name.lower()):
                ui.append('avail', 
                    UI.AppButton(
                        id=y.id,
                        name=y.name,
                        iconfont=y.icon,
                        version=y.version
                        )
                    )

        if self._info:
            info = [x for x in self._mgr.available if x.id==self._info][0]
            if info.assets:
                try:
                    data = send_json('https://%s/' % self.app.gconfig.get('genesis', 'update_server'), 
                        {'get': 'assets', 'id': info.id})
                    ui.find('app-logo').append(UI.Image(file="data:image/png;base64,%s" % data['logo'], cls='app-logo'))
                    for x in data['screenshots']:
                        ui.find('app-screens').append(UI.Image(file="data:image/jpeg;base64,%s" % x, cls="img-responsive img-thumbnail app-screenshot", lightbox=self._info))
                except:
                    pass
            ui.find('app-short').set('text', info.description)
            ui.find('app-version').set('text', info.version)
            ui.find('app-cats').set('text', '; '.join(['%s: %s'%(x['primary'], ', '.join(x['secondary'])) for x in info.categories]))
            ui.find('app-name').set('text', info.name)
            ui.find('app-desc').set('text', info.long_description)
            if info.app_author:
                ui.find('app-plugauthor').set('text', info.app_author)
                ui.find('app-plughomepage').set('text', info.app_homepage)
                ui.find('app-plughomepage').set('url', info.app_homepage)
            else:
                ui.remove('app-plugauth')
            ui.find('app-author').set('text', info.author)
            ui.find('app-homepage').set('text', info.homepage)
            ui.find('app-homepage').set('url', info.homepage)
        else:
            ui.remove('dlgInfo')

        if self._metoo:
            for x in self._metoo:
                ui.append('prereqs', UI.DTR(
                    UI.DTD(UI.IconFont(iconfont=x[1].icon), width='1'),
                    UI.DTD(UI.Label(text=x[0], bold=True)),
                    UI.DTD(UI.Label(text=x[1].name))
                ))
        else:
            ui.remove('dlgMeToo')

        return ui

    def get_ui_upload(self):
        return UI.Uploader(
            url='/upload_plugin',
            text='Install'
        )

    @url('^/upload_plugin$')
    def upload(self, req, sr):
        vars = get_environment_vars(req)
        f = vars.getvalue('file', None)
        try:
            self._mgr.install_stream(f)
        except:
            pass
        sr('301 Moved Permanently', [('Location', '/')])
        return ''

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'update':
            try:
                self._mgr.update_list(crit=True)
            except Exception, e:
                self.put_message('err', str(e))
                self.app.log.error(str(e))
            else:
                self.put_message('success', 'Application list updated')
        elif params[0] == 'remove':
            metoo = self._mgr.check_conflict(params[1], 'remove')
            if metoo:
                self._metoo = metoo
                self._metoo.append(('Remove', next(x for x in self._mgr.installed if x.id == params[1])))
            else:
                try:
                    self._mgr.remove(params[1], self)
                    self._nc.remove(params[1])
                except Exception, e:
                    self.put_message('err', str(e))
                finally:
                    self.put_message('success', 'Application removed successfully.')
        elif params[0] == 'info':
            self._info = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgInfo':
            if vars.getvalue('action', '') == 'OK':
                metoo = self._mgr.check_conflict(self._info, 'install')
                if metoo:
                    self._metoo = metoo
                    self._metoo.append(('Install', next(x for x in self._mgr.available if x.id == self._info)))
                else:
                    try:
                        self.install(self._info)
                    except Exception, e:
                        self.put_message('err', str(e))
                    finally:
                        self.put_message('success', 'Application installed successfully!')
            self._info = None
        elif params[0] == 'dlgMeToo':
            if vars.getvalue('action', '') == 'OK':
                success = False
                try:
                    for x in self._metoo:
                        if x[0] == 'Install':
                            self.install(x[1].id)
                            success = 'installed'
                        elif x[0] == 'Remove':
                            self._mgr.remove(x[1].id, self)
                            self._nc.remove(x[1].id)
                            success = 'removed'
                except Exception, e:
                    success = False
                    self.put_message('err', str(e))
                if success:
                    self.put_message('success', 'Applications %s successfully.' % success)
            self._metoo = []

    def install(self, id):
        self._mgr.install(id, True, self)
        ComponentManager.get().rescan()
        ConfManager.get().rescan()
        self._nc.refresh()
