from genesis.com import *
from genesis.api import *
from genesis.plugins.core.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *
from genesis.plugins.databases.utils import *
from genesis.plugins.network.backend import IHostnameManager

import re

from backend import WebappControl, ReloadError
from api import Webapp


class WebAppsPlugin(apis.services.ServiceControlPlugin):
    text = 'Websites'
    iconfont = 'gen-earth'
    folder = None
    services = []

    def on_init(self):
        self.services = []
        self.ncops = apis.networkcontrol(self.app)
        self.apiops = apis.webapps(self.app)
        self.dbops = apis.databases(self.app)
        self.mgr = WebappControl(self.app)
        self.sites = sorted(self.apiops.get_sites(), 
            key=lambda st: st.name)
        ats = sorted([x.plugin_info for x in self.apiops.get_apptypes()], key=lambda x: x.name.lower())
        self.apptypes = sorted(ats, key=lambda x: (hasattr(x, 'sort')))
        if len(self.sites) != 0:
            self.services.append(
                {
                    "name": 'Web Server',
                    "binary": 'nginx',
                    "ports": []
                }
            )
            for x in self.sites:
                if x.php:
                    self.services.append(
                        {
                            "name": 'PHP FastCGI',
                            "binary": 'php-fpm',
                            "ports": []
                        }
                    )
                    break
        if not self._current:
            self._current = self.apptypes[0] if len(self.apptypes) else None
        for apptype in self.apptypes:
            ok = False
            for site in self.sites:
                if site.stype == apptype.wa_plugin:
                    ok = True
            if ok == False:
                continue
            if hasattr(apptype, 'services'):
                for dep in apptype.services:
                    post = True
                    for svc in self.services:
                        if svc['binary'] == dep['binary']:
                            post = False
                    if post == True:
                        self.services.append({"name": dep['name'], "binary": dep['binary'], "ports": []})

    def on_session_start(self):
        self._add = None
        self._edit = None
        self._setup = None
        self._settings = None
        self._dbauth = ('','','')

    def get_main_ui(self):
        ui = self.app.inflate('webapps:main')

        for s in self.sites:
            if s.addr and s.ssl:
                addr = 'https://' + s.addr + (':'+s.port if s.port != '443' else '')
            elif s.addr:
                addr = 'http://' + s.addr + (':'+s.port if s.port != '80' else '')
            else:
                addr = False

            update = False
            if s.version and (s.version != 'None' or (hasattr(s.sclass, 'plugin_info') and s.sclass.plugin_info.website_updates)) \
            and s.version != s.sclass.plugin_info.version.rsplit('-', 1)[0]:
                update = True

            ui.find('main').append(
                UI.TblBtn(
                    UI.TipIcon(
                        iconfont='gen-download',
                        id=('update/') + str(self.sites.index(s)),
                        text='Update Site'
                    ) if update else None,
                    UI.TipIcon(
                        iconfont='gen-minus-circle' if s.enabled else 'gen-checkmark-circle',
                        id=('disable/' if s.enabled else 'enable/') + str(self.sites.index(s)),
                        text='Disable' if s.enabled else 'Enable'
                    ),
                    UI.TipIcon(
                        iconfont='gen-tools',
                        id='config/' + str(self.sites.index(s)),
                        text='Configure'
                    ),
                    UI.TipIcon(
                        iconfont='gen-cancel-circle',
                        id='drop/' + str(self.sites.index(s)),
                        text='Delete',
                        warning='Are you sure you wish to delete site %s? This action is irreversible.%s'%(s.name,
                            ' If this Reverse Proxy was set up automatically by Genesis, this may cause the associated plugin to stop functioning.' if s.stype == 'ReverseProxy' else '')
                    ),
                    id=s.name,
                    outlink=addr,
                    icon=s.sclass.plugin_info.icon if s.sclass and hasattr(s.sclass.plugin_info, 'icon') else 'gen-earth',
                    name=s.name,
                    subtext=s.stype
                    )
                )
        ui.find('main').append(
            UI.TblBtn(
                id='add',
                icon='gen-plus-circle',
                name='Add new site'
                )
            )

        provs = ui.find('provs')

        for apptype in self.apptypes:
            provs.append(
                    UI.ListItem(
                        UI.Label(text=apptype.name),
                        iconfont=apptype.icon,
                        id=apptype.name,
                        active=apptype.name==self._current.name
                    )
                )

        info = self._current
        if info:
            if info.logo:
                ui.find('logo').append(UI.Image(file='/dl/'+self._current.id+'/logo.png'))
            ui.find('appname').set('text', info.name)
            ui.find('short').set('text', info.desc)
            if info.app_homepage is None:
                ui.find('website').set('text', 'None')
                ui.find('website').set('url', 'http://localhost')
            else:
                ui.find('website').set('text', info.app_homepage)
                ui.find('website').set('url', info.app_homepage)
            ui.find('desc').set('text', info.longdesc)

        if self._add is None:
            ui.remove('dlgAdd')

        if self._setup is not None:
            ui.find('addr').set('value', self.app.get_backend(IHostnameManager).gethostname().lower())
            if len(self._setup.dbengines) > 1:
                ui.append('app-config', UI.Formline(
                    UI.SelectInput(
                        *list(UI.SelectOption(text=x if x else 'None', value=x if x else 'None') for x in self._setup.dbengines), 
                        name="dbtype", id="dbtype"), 
                    text="Database Type", 
                    help="This application supports multiple types of databases. Please choose the one you would like to use.")
                )
            if self._setup.dbengines:
                ui.append('app-config', UI.Formline(UI.TextInput(name="dbname", id="dbname"), text="Database Name (Optional)"))
                ui.append('app-config', UI.Formline(UI.TextInput(name="dbpass", id="dbpass", password=True), text="Database User Password (Optional)"))
            try:
                cfgui = self.app.inflate(self._setup.id + ':conf')
                ui.append('app-config', UI.Label(size=3, text="App Settings"))
                if hasattr(self.apiops.get_interface(self._setup.wa_plugin), 'show_opts_add'):
                    self.apiops.get_interface(self._setup.wa_plugin).show_opts_add(cfgui)
                ui.append('app-config', cfgui)
            except:
                pass
        else:
            ui.remove('dlgSetup')

        if self._edit is not None:
            try:
                edgui = self.app.inflate(self._edit.stype.lower() + ':edit')
                ui.append('dlgEdit', edgui)
            except:
                pass
            ui.find('cfgname').set('value', self._edit.name)
            ui.find('cfgaddr').set('value', self._edit.addr)
            ui.find('cfgport').set('value', self._edit.port)
        else:
            ui.remove('dlgEdit')

        if self._dbauth[0] and not self.dbops.get_interface(self._dbauth[1]).checkpwstat():
            self.put_message('err', '%s does not have a root password set. '
                'Please add this via the Databases screen.' % self._dbauth[1])
            self._dbauth = ('','','')
        if self._dbauth[0]:
            ui.append('main', 
                UI.Authorization(
                    app='Webapps',
                    reason='%s a website'%('Adding' if self._dbauth[0] == 'add' else 'Removing'),
                    label='Please enter your %s root password'%self._dbauth[1])
                )

        if self._settings:
            size = re.search("client_max_body_size\s*([^\s]+)[mM];", open('/etc/nginx/nginx.conf', 'r').read())
            size = size.group(1) if size else "1"
            ui.append('main',
                UI.DialogBox(
                    UI.Formline(UI.TextInput(id="uplsize", name="uplsize", value=size), 
                        text="Max file upload size (MB)"),
                    id="dlgSettings")
                )

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            if self.apptypes == []:
                self.put_message('err', 'No webapp types installed. Check the Applications tab to find some')
            else:
                self._add = len(self.sites)
        elif params[0] == 'config':
            self._edit = self.sites[int(params[1])]
        elif params[0] == 'drop':
            site = self.sites[int(params[1])]
            if hasattr(site, 'dbengine') and site.dbengine and \
            self.dbops.get_info(site.dbengine).requires_conn and \
            not self.dbops.get_dbconn(site.dbengine):
                self._dbauth = ('drop', site.dbengine, site)
            else:
                try:
                    self.mgr.remove(self, site)
                except Exception, e:
                    self.put_message('err', 'Website removal failed: ' + str(e))
                    self.app.log.error('Website removal failed: ' + str(e))
                else:
                    self.put_message('success', 'Website successfully removed')
                    self.ncops.remove_webapp(site.name)
        elif params[0] == 'enable':
            self.mgr.nginx_enable(self.sites[int(params[1])])
        elif params[0] == 'disable':
            self.mgr.nginx_disable(self.sites[int(params[1])])
        elif params[0] == 'update':
            s = self.sites[int(params[1])]
            w = next(x for x in self.apptypes if x.name==s.stype)
            self.mgr.update(self, w, s)
        elif params[0] == 'settings':
            self._settings = True
        else: 
            for x in self.apptypes:
                if x.name.lower() == params[0]:
                    speccall = getattr(self.apiops.get_interface(x.wa_plugin), params[1])
                    speccall(self._edit)

    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgSettings':
            if vars.getvalue('action', '') == 'OK':
                size = vars.getvalue('uplsize', '10')
                f = open('/etc/nginx/nginx.conf', 'r')
                data = f.readlines()
                f.close()
                if 'client_max_body_size' in ''.join(data):
                    for x in enumerate(data):
                        if "client_max_body_size" in x[1]:
                            data[x[0]] = "\tclient_max_body_size %sM;\n" % size
                else:
                    for x in enumerate(data):
                        if 'http {' in x[1]:
                            data.insert(x[0]+1, '\tclient_max_body_size %sM;\n' % size)
                phpctl = apis.langassist(self.app).get_interface('PHP')
                if phpctl:
                    phpctl.upload_size(size)
                open('/etc/nginx/nginx.conf', 'w').writelines(data)
                self.mgr.nginx_reload()
                self.put_message("success", "Settings saved successfully")
            self._settings = None
        if params[0] == 'dlgAdd':
            if vars.getvalue('action', '') == 'OK':
                self._setup = self._current
            self._add = None
        if params[0] == 'dlgEdit':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('cfgname', '')
                addr = vars.getvalue('cfgaddr', '')
                port = vars.getvalue('cfgport', '')
                vaddr = True
                for site in self.sites:
                    if addr == site.addr and port == site.port:
                        vaddr = False
                if name == '':
                    self.put_message('err', 'Must choose a name')
                elif re.search('\.|-|`|\\\\|\/|^test$|[ ]', name):
                    self.put_message('err', 'Site name must not contain spaces, dots, dashes or special characters')
                elif addr == '':
                    self.put_message('err', 'Must choose an address')
                elif port == '':
                    self.put_message('err', 'Must choose a port (default 80)')
                elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
                    self.put_message('err', 'Can\'t use the same port number as Genesis')
                elif not vaddr:
                    self.put_message('err', 'Site must have either a different domain/subdomain or a different port')
                elif self._edit.ssl and port == '80':
                    self.put_message('err', 'Cannot set an HTTPS site to port 80')
                elif not self._edit.ssl and port == '443':
                    self.put_message('err', 'Cannot set an HTTP-only site to port 443')
                else:
                    w = Webapp()
                    w.name = name
                    w.stype = self._edit.stype
                    w.path = self._edit.path
                    w.addr = addr
                    w.port = port
                    w.ssl = self._edit.ssl
                    w.php = self._edit.php
                    try:
                        self.mgr.nginx_edit(self._edit, w)
                    except ReloadError, e:
                        self.put_message("warn", str(e))
                    else:
                        self.ncops.change_webapp(self._edit, w)
                        self.put_message('success', 'Site edited successfully')
            self._edit = None
        if params[0] == 'dlgSetup':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('name', '').lower()
                addr = vars.getvalue('addr', '')
                port = vars.getvalue('port', '80')
                vname, vaddr = True, True
                for site in self.sites:
                    if name == site.name:
                        vname = False
                    if addr == site.addr and port == site.port:
                        vaddr = False
                if not name or not self._setup:
                    self.put_message('err', 'Name or type not selected')
                elif re.search('\.|-|`|\\\\|\/|^test$|[ ]', name):
                    self.put_message('err', 'Site name must not contain spaces, dots, dashes or special characters')
                elif addr == '':
                    self.put_message('err', 'Must choose an address')
                elif port == '':
                    self.put_message('err', 'Must choose a port (default 80)')
                elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
                    self.put_message('err', 'Can\'t use the same port number as Genesis')
                elif not vaddr:
                    self.put_message('err', 'Site must have either a different domain/subdomain or a different port')
                elif not vname:
                    self.put_message('err', 'A site with this name already exists')
                elif (not hasattr(self._setup, 'dbengines') or not self._setup.dbengines) \
                or (vars.has_key('dbtype') and vars.getvalue('dbtype', '') in ['', 'None']):
                    self.addsite(self._setup, vars, {}, True)
                    self._setup = None
                elif hasattr(self._setup, 'dbengines') and self._setup.dbengines:
                    if vars.getvalue('dbtype', ''):
                        self._setup.selected_dbengine = vars.getvalue('dbtype', '')
                    elif not hasattr(self._setup, 'selected_dbengine'):
                        self._setup.selected_dbengine = self._setup.dbengines[0]
                    dbengine = self._setup.selected_dbengine
                    on = False
                    for dbtype in self.dbops.get_dbtypes():
                        if dbengine == dbtype[0] and dbtype[2] == True:
                            on = True
                        elif dbengine == dbtype[0] and dbtype[2] == None:
                            on = True
                    if on:
                        if self.dbops.get_info(dbengine).requires_conn and \
                        not self.dbops.get_dbconn(dbengine):
                            self._dbauth = ('add', dbengine, self._setup, vars)
                            self._setup = None
                        else:
                            if vars.getvalue('dbname') and vars.getvalue('dbpass'):
                                try:
                                    self.dbops.get_interface(dbengine).validate(
                                        vars.getvalue('dbname'), vars.getvalue('dbname'), 
                                        vars.getvalue('dbpass'), self.dbops.get_dbconn(dbengine))
                                except Exception, e:
                                    self.put_message('err', str(e))
                                    return
                            elif vars.getvalue('dbname'):
                                self.put_message('err', 'You must enter a database password if you specify a database name!')
                                return
                            elif vars.getvalue('dbpass'):
                                self.put_message('err', 'You must enter a database name if you specify a database password!')
                                return
                            self.addsite(self._setup, vars, 
                                {'engine': dbengine, 'name': vars.getvalue('dbname', vars.getvalue('name')), 
                                'user': vars.getvalue('dbname', vars.getvalue('name')), 
                                'passwd': vars.getvalue('dbpass', '')}, True)
                            self._setup = None
                    else:
                        self.put_message('err', 'The database engine for %s is not running. Please start it via the Status button.' % dbengine)
                        self._setup = None
            else:
                self._setup = None
        if params[0] == 'dlgAuthorize':
            if vars.getvalue('action', '') == 'OK':
                login = vars.getvalue('auth-string', '')
                try:
                    dbauth = self._dbauth
                    self._dbauth = ('','','')
                    self.dbops.get_interface(dbauth[1]).connect(
                        store=self.app.session['dbconns'],
                        passwd=login)
                    if dbauth[0] == 'drop':
                        try:
                            self.mgr.remove(self, dbauth[2])
                        except Exception, e:
                            self.put_message('err', 'Website removal failed: ' + str(e))
                            self.app.log.error('Website removal failed: ' + str(e))
                        else:
                            self.put_message('success', 'Website successfully removed')
                            self.ncops.remove_webapp(dbauth[2].name)
                    elif dbauth[0] == 'add':
                        if dbauth[3].getvalue('dbname') and dbauth[3].getvalue('dbpass'):
                            try:
                                self.dbops.get_interface(dbauth[1]).validate(
                                    dbauth[3].getvalue('dbname'), dbauth[3].getvalue('dbname'), 
                                    dbauth[3].getvalue('dbpass'), self.dbops.get_dbconn(dbauth[1]))
                            except Exception, e:
                                self.put_message('err', str(e))
                                self._setup = dbauth[2]
                                return
                        elif dbauth[3].getvalue('dbname'):
                            self.put_message('err', 'You must enter a database password if you specify a database name!')
                            self._setup = dbauth[2]
                            return
                        elif dbauth[3].getvalue('dbpass'):
                            self.put_message('err', 'You must enter a database name if you specify a database password!')
                            self._setup = dbauth[2]
                            return
                        self.addsite(dbauth[2], dbauth[3], 
                            {'engine': dbauth[1], 'name': dbauth[3].getvalue('dbname'), 
                            'user': dbauth[3].getvalue('dbname'), 
                            'passwd': dbauth[3].getvalue('dbpass', '')}, True)
                except DBAuthFail, e:
                    self.put_message('err', str(e))
            else:
                self.put_message('info', 'Website %s cancelled' % self._dbauth[0])
                self._dbauth = ('','','')

    def addsite(self, stype, vars, dbinfo={}, enable=True):
        name = vars.getvalue('name')
        port = vars.getvalue('port', '80')
        try:
            spmsg = self.mgr.add(self, stype, vars, dbinfo, enable)
        except Exception, e:
            self.put_message('err', str(e))
            self.app.log.error(str(e))
        else:
            self.put_message('success', '%s added sucessfully' % name)
            self.ncops.add_webapp((name, stype.name, port))
            if spmsg:
                self.put_message('info', spmsg)

    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        for p in self.apptypes:
            if p.name == params[0]:
                self._current = p
