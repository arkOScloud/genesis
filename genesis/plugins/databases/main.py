from genesis.api import *
from genesis.ui import *
from genesis import apis

from utils import *


class DatabasesPlugin(apis.services.ServiceControlPlugin, URLHandler):
    text = 'Databases'
    iconfont = 'gen-database'
    folder = 'tools'
    services = []

    def on_init(self):
        self.dbops = apis.databases(self.app)
        self.dbs = sorted(self.dbops.get_databases(), 
            key=lambda db: (db['type'], db['name']))
        self.users = sorted(self.dbops.get_users(), 
            key=lambda db: (db['type'], db['name']))
        self.dbtypes = sorted(self.dbops.get_dbtypes(), 
            key=lambda db: db[0])
        for dbtype in self.dbtypes:
            ok = True
            if not dbtype[1]:
                ok = False
            for svc in self.services:
                if svc['binary'] == dbtype[1]:
                    ok = False
            if ok == True:
                self.services.append(
                    {
                        "name": dbtype[0], 
                        "binary": dbtype[1],
                        "ports": []
                    }
                )

    def on_session_start(self):
        self._tab = 0
        self._add = None
        self._useradd = None
        self._chmod = None
        self._info = None
        self._exec = None
        self._import = None
        self._input = None
        self._output = None
        self._rootpwds = {}
        self._cancelauth = []

    def get_main_ui(self):
        ui = self.app.inflate('databases:main')
        ui.find('tabs').set('active', self._tab)
        t = ui.find('list')
        ut = ui.find('usrlist')
        st = ui.find('settings')

        ubutton = False
        for dbtype in self.dbtypes:
            if dbtype[2] is False:
                self.put_message('err', 'The %s database process is not '
                    'running. Your databases/users for this type will not '
                    'appear until you start the process.' % dbtype[0])
                self.dbtypes.remove(dbtype)
            else:
                if self.dbops.get_info(dbtype[0]).requires_conn == True and \
                not self.dbops.get_interface(dbtype[0]).checkpwstat():
                    self._rootpwds[dbtype[0]] = False
                    self.put_message('err', '%s does not have a root password set. '
                        'Please add this via the Settings tab.' % dbtype[0])
                    ubutton = True
                elif not dbtype[0] in self._cancelauth and \
                self.dbops.get_info(dbtype[0]).requires_conn == True and \
                not self.dbops.get_dbconn(dbtype[0]):
                    ui.append('main', 
                        UI.Authorization(
                            app='Databases',
                            reason='Unlock %s database engine'%dbtype[0],
                            label='Please enter your %s root password'%dbtype[0],
                            meta=dbtype[0])
                    )
                    self._rootpwds[dbtype[0]] = True
                elif self.dbops.get_info(dbtype[0]).multiuser == True:
                    self._rootpwds[dbtype[0]] = True
                    ubutton = True
                else:
                    self._rootpwds[dbtype[0]] = True

        for d in self.dbs:
            ui.find('dblist').append(
                UI.TblBtn(
                    UI.TipIcon(
                        iconfont='gen-target',
                        id='exec/'+str(self.dbs.index(d)),
                        text='Execute'
                    ),
                    UI.TipIcon(
                        iconfont='gen-download',
                        onclick='window.open("/db/s/%s/%s", "_blank");'%(d['type'], d['name']),
                        text='Download SQL Dump'
                    ),
                    id='info/'+str(self.dbs.index(d)),
                    icon='gen-database',
                    name=d['name'],
                    subtext=d['type']
                    )
                )
        ui.find('dblist').append(
            UI.TblBtn(
                id='add',
                icon='gen-plus-circle',
                name='Add database'
                )
            )

        for u in self.users:
            ui.find('uslist').append(
                UI.TblBtn(
                    UI.TipIcon(
                        iconfont='gen-tools',
                        id='chmod/' + str(self.users.index(u)),
                        text='Grant/Revoke Permissions'
                    ),
                    UI.TipIcon(
                        iconfont='gen-cancel-circle',
                        id='deluser/' + str(self.users.index(u)),
                        text='Delete',
                        warning='Are you sure you wish to delete user %s? This may prevent any applications using it from functioning properly.'%u['name']
                    ),
                    id=u['name'],
                    icon='gen-user',
                    name=u['name'],
                    subtext=u['type'],
                    action='none'
                    )
                )
        if ubutton == True:
            ui.find('uslist').append(
                UI.TblBtn(
                    id='adduser',
                    icon='gen-user-plus',
                    name='Add user'
                    )
                )

        for dbtype in self.dbtypes:
            if self.dbops.get_info(dbtype[0]).multiuser:
                st.append(UI.Label(text=dbtype[0], size='5'))
            if self.dbops.get_info(dbtype[0]).multiuser and dbtype[0] in self._cancelauth:
                st.append(UI.Label(text='You must authenticate before changing these settings.'))
            elif self.dbops.get_info(dbtype[0]).multiuser:
                st.append(UI.SimpleForm(
                    UI.Formline(UI.TextInput(id='newpasswd', name="newpasswd", password=True, verify="password", verifywith="newpasswd"),
                        text="New root password", feedback="gen-lock", iid="newpasswd"
                    ),
                    UI.Formline(UI.TextInput(id='newpasswdb', name="newpasswdb", password=True, verify="password", verifywith="newpasswd"),
                        text="Confirm root password", feedback="gen-lock", iid="newpasswdb"
                    ),
                    UI.Formline(UI.Btn(onclick="form", form="frmPasswd%s" % dbtype[0],
                        design="primary", action="OK", text="Change Password")),
                    id="frmPasswd%s" % dbtype[0]
                ))
            if self.dbops.get_info(dbtype[0]).requires_conn:
                st.append(UI.Formline(UI.Btn(text='Reauthenticate', id='reauth/'+dbtype[0])))

        type_sel_all = [UI.SelectOption(text = x[0], value = x[0])
            for x in self.dbtypes if x[0] not in self._cancelauth]
        type_sel_multiuser = [UI.SelectOption(text = x[0], value = x[0])
            for x in self.dbtypes if x[0] not in self._cancelauth and \
            self.dbops.get_info(x[0]).multiuser]
        if not type_sel_multiuser:
            ubutton = False

        if self._add and type_sel_all:
            ui.appendAll('type', *type_sel_all)
        else:
            ui.remove('dlgAdd')

        if self._info:
            ui.find('dlgInfo').set('miscbtnid', 'drop/' + str(self.dbs.index(self._info)))
            ui.find('idbname').set('text', self._info['name'])
            ui.find('idbtype').set('text', self._info['type'])
            cls = self.dbops.get_interface(self._info['type'])
            if cls.plugin_info.requires_conn:
                ui.find('idbsize').set('text', cls.get_size(self._info['name'], self.app.session['dbconns'][self._info['type']]))
            else:
                ui.find('idbsize').set('text', cls.get_size(self._info['name']))
        else:
            ui.remove('dlgInfo')

        if self._exec:
            edlg = self.app.inflate('databases:execute')
            edlg.find('dlgExec').set('title', 'Execute on database %s' % self._exec['name'])
            edlg.find('dlgExec').set('miscbtnid', 'uplsql/' + str(self.dbs.index(self._exec)))
            if self._input is not None:
                elem = edlg.find('input')
                elem.set('value', self._input)
            if self._output is not None:
                elem = edlg.find('output')
                elem.set('value', self._output)
            ui.append('main', edlg)

        if self._useradd:
            ui.appendAll('usertype', *type_sel_multiuser)
        else:
            ui.remove('dlgAddUser')

        if self._chmod:
            iface = self.dbops.get_interface(self._chmod['type'])
            plist = iface.chperm('', self._chmod['name'], 'check')
            dblist = [UI.SelectOption(text=x['name'], value=x['name'])
                for x in iface.get_dbs()]
            ui.find('permlist').set('value', plist)
            ui.appendAll('pdblist', *dblist)
        else:
            ui.remove('dlgChmod')

        if self._import:
            ui.append('main', UI.UploadBox(text="Uploading SQL to %s" % self._import['name'], id="dlgImport"))

        return ui

    @url('^/db/s/.*$')
    def download(self, req, start_response):
        params = req['PATH_INFO'].split('/')[3:]
        iface = apis.databases(self.app).get_interface(params[0])
        if iface.plugin_info.requires_conn:
            d = iface.dump(params[1], self.app.session['dbconns'][params[0]])
        else:
            d = iface.dump(params[1])
        start_response('200 OK', [
            ('Content-length', str(len(d.encode('utf-8')))),
            ('Content-Disposition', 'attachment; filename=%s'%params[1]+'.sql')
        ])
        return d

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            if self.dbtypes == []:
                self.put_message('err', 'No database engines installed. Check the Applications tab to find some')
            else:
                self._add = True
            self._tab = 0
        if params[0] == 'adduser':
            self._useradd = True
            self._tab = 1
        if params[0] == 'info':
            self._info = self.dbs[int(params[1])]
            self._tab = 0
        if params[0] == 'exec':
            self._exec = self.dbs[int(params[1])]
            self._input = None
            self._output = None
            self._tab = 0
        if params[0] == 'chmod':
            u = self.users[int(params[1])]
            if self.dbops.get_interface(u['type']).get_dbs():
                self._chmod = u
            else:
                self.put_message("err", "No applicable databases found for this engine")
            self._tab = 1
        if params[0] == 'uplsql':
            self._import = self._exec
            self._exec = None
            self._tab = 0
        if params[0] == 'drop':
            self._tab = 0
            try:
                dt = self.dbs[int(params[1])]
                cls = self.dbops.get_interface(dt['type'])
                if cls.plugin_info.requires_conn:
                    cls.remove(dt['name'], self.app.session['dbconns'][dt['type']])
                else:
                    cls.remove(dt['name'])
            except Exception, e:
                self.put_message('err', 'Database drop failed: ' + str(e))
                self.app.log.error('Database drop failed: ' + str(e))
            else:
                self._info = None
                self.put_message('success', 'Database successfully dropped')
        if params[0] == 'deluser':
            self._tab = 1
            try:
                dt = self.users[int(params[1])]
                iface = self.dbops.get_interface(dt['type'])
                iface.usermod(dt['name'], 'del', '')
            except Exception, e:
                self.put_message('err', 'User drop failed: ' + str(e))
                self.app.log.error('User drop failed: ' + str(e))
            else:
                self.put_message('success', 'User deleted') 
        if params[0] == 'reauth':
            if params[1] in self._cancelauth:
                self._cancelauth.remove(params[1])
            self.dbops.clear_dbconn(params[1])

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgAdd':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('name', '')
                dbtype = vars.getvalue('type', '')
                if not name or not dbtype:
                    self.put_message('err', 'Name or type not selected')
                elif self._rootpwds.has_key(dbtype) and self._rootpwds[dbtype] == False:
                    self.put_message('err', 'Please add a root password for this database type via the Settings tab first.')
                else:
                    cls = self.dbops.get_interface(dbtype)
                    try:
                        if cls.plugin_info.requires_conn:
                            cls.add(name, self.app.session['dbconns'][dbtype])
                        else:
                            cls.add(name)
                    except Exception, e:
                        self.put_message('err', 'Database add failed: ' 
                            + str(e))
                        self.app.log.error('Database add failed: ' 
                            + str(e))
                    else:
                        self.put_message('success', 
                            'Database %s added sucessfully' % name)
            self._add = None
        elif params[0] == 'dlgExec':
            if vars.getvalue('action', '') == 'OK':
                self._input = vars.getvalue('input', '')
                iface = self.dbops.get_interface(self._exec['type'])
                try:
                    self._output = iface.execute(self._exec['name'], self._input)
                except Exception, e:
                    self.put_message('err', str(e))
            else:
                self._exec = None
        elif params[0] == 'dlgInfo':
            self._info = None
        elif params[0] == 'dlgImport':
            if vars.getvalue('action', '') == 'OK' and vars.has_key('file'):
                iface = self.dbops.get_interface(self._import['type'])
                try:
                    self._output = iface.execute(self._import['name'], vars['file'].value)
                    self.put_message('success', 'SQL import completed successfully')
                except Exception, e:
                    self.put_message('err', str(e))
            self._import = None
        elif params[0] == 'dlgAddUser':
            if vars.getvalue('action', '') == 'OK':
                username = vars.getvalue('username')
                passwd = vars.getvalue('passwd')
                usertype = vars.getvalue('usertype', '')
                if not username or not usertype:
                    self.put_message('err', 'Name or type not selected')
                elif self._rootpwds[usertype] == False:
                    self.put_message('err', 'Please add a root password for this database type via the Settings tab first.')
                else:
                    try:
                        iface = self.dbops.get_interface(usertype)
                        iface.usermod(username, 'add', passwd)
                    except Exception, e:
                        self.put_message('err', 'User add failed: '
                            + str(e))
                        self.app.log.error('User add failed: '
                            + str(e))
                    else:
                        self.put_message('success',
                            'User %s added successfully' % username)
            self._useradd = None
        elif params[0] == 'dlgChmod':
            if vars.getvalue('action', '') == 'OK':
                action = vars.getvalue('chperm', '')
                dbname = vars.getvalue('pdblist', '')
                try:
                    iface = self.dbops.get_interface(self._chmod['type'])
                    iface.chperm(dbname, self._chmod['name'], action)
                except Exception, e:
                    self.put_message('err', 'Permission change failed, see logs')
                    self.app.log.error('Permission change failed: '
                        + str(e))
                else:
                    self.put_message('success',
                        'Permissions for %s changed successfully' % self._chmod['name'])
            self._chmod = None
        elif params[0] == 'dlgAuthorize':
            dbtype = vars.getvalue('auth-metadata', '')
            if vars.getvalue('action', '') == 'OK':
                login = vars.getvalue('auth-string', '')
                try:
                    self.dbops.get_interface(dbtype).connect(
                        store=self.app.session['dbconns'],
                        passwd=login)
                except DBAuthFail, e:
                    self.put_message('err', str(e))
            else:
                self.put_message('err', 'You refused to authenticate to %s. '
                    'You will not be able to perform operations with this database type. '
                    'Go to Settings and click Reauthenticate to retry.' % dbtype)
                self._cancelauth.append(dbtype)
        elif params[0].startswith('frmPasswd'):
            dbtype = params[0].split('frmPasswd')[1]
            v = vars.getvalue('newpasswd')
            if v != vars.getvalue('newpasswdb',''):
                self.put_message('err', 'Passwords must match')
            else:
                try:
                    if not self.app.session.has_key('dbconns'):
                        self.app.session['dbconns'] = {}
                    if not self.dbops.get_interface(dbtype).checkpwstat():
                        self.dbops.get_interface(dbtype).connect(
                            store=self.app.session['dbconns'],
                            passwd='')
                    self.dbops.get_interface(dbtype).chpwstat(
                        vars.getvalue('newpasswd'),
                        self.app.session['dbconns'][dbtype]
                        )
                    self.put_message('success', 'Password for %s changed successfully' % dbtype)
                except Exception, e:
                    self.put_message('err', 'Error changing password for %s: %s' % (dbtype, str(e)))
            self._tab = 2
