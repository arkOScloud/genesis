import re

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager

import backend

class RadicalePlugin(apis.services.ServiceControlPlugin):
    text = 'Calendar'
    iconfont = 'gen-calendar'
    folder = 'servers'

    def on_session_start(self):
        self._config = backend.RadicaleConfig(self.app)
        self._wa = apis.webapps(self.app)
        self._rc = backend.RadicaleControl(self.app)
        self._add = None
        self._edit = None

    def on_init(self):
        self.services = []
        self._users = self._rc.list_users()
        self.site = filter(lambda x: x.name=='radicale', self._wa.get_sites())
        if self.site:
            self.site = self.site[0]
        else:
            self.site = None

    def get_main_ui(self):
        is_installed = self._rc.is_installed()
        if not self.app.get_config(self._config).first_run_complete \
        or is_installed == 'no':
            ui = self.app.inflate('radicale:setup')
            ui.find('addr').set('value', self.app.get_backend(IHostnameManager).gethostname())
            if is_installed == 'no':
                self.put_message('err', 'Your Calendar/Contacts server does not appear to be properly configured. Please rerun this setup.')
            return ui
        ui = self.app.inflate('radicale:main')

        url = 'http%s://%s%s'%('s' if self.site.ssl else '', self.site.addr, ':'+self.site.port if self.site.port not in ['80', '443'] else '')
        if is_installed == 'off':
            ui.find('rinfo').append(
                UI.Label(size='1', bold=True,
                    text='Your Calendar/Contacts server is installed but not running. Please start it via the Status button.')
                )
        else:
            ui.find('rinfo').append(
                UI.Label(size='1', bold=True,
                    text='Your Calendar/Contacts server is listening at '),
                )
            ui.find('rinfo').append(UI.OutLinkLabel(text=url, url=url))

        for u in self._users:
            ui.find('main').append(
                UI.TblBtn(
                    UI.TipIcon(
                        iconfont='gen-cancel-circle', 
                        id='del/'+str(self._users.index(u)), 
                        text='Delete', 
                        warning='Are you sure you want to delete calendar user %s?'%u
                    ),
                    id='edit/'+str(self._users.index(u)),
                    icon='gen-user',
                    name=u,
                    subtext='User'
                    )
                )
        ui.find('main').append(
            UI.TblBtn(
                id='add',
                icon='gen-user-plus',
                name='Add user'
                )
            )

        if self._add:
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.TextInput(name='acct', id='acct'),
                        text='Username', feedback="gen-user", iid="acct"
                    ),
                    UI.Formline(UI.TextInput(id='passwd', name="passwd", password=True, verify="password", verifywith="passwd"),
                        text="Password", feedback="gen-lock", iid="passwd"
                    ),
                    UI.Formline(UI.TextInput(id='passwdb', name="passwdb", password=True, verify="password", verifywith="passwd"),
                        text="Confirm password", feedback="gen-lock", iid="passwdb"
                    ),
                    id='dlgAddUser', title="Creating new Calendar/Contacts user")
                )

        if self._edit:
            ui.append('main',
                UI.DialogBox(
                    UI.Formline(UI.TextInput(id='chpasswd', name="chpasswd", password=True, verify="password", verifywith="chpasswd"),
                        text="New password", feedback="gen-lock", iid="chpasswd"
                    ),
                    UI.Formline(UI.TextInput(id='chpasswdb', name="chpasswdb", password=True, verify="password", verifywith="chpasswd"),
                        text="Confirm password", feedback="gen-lock", iid="chpasswdb"
                    ),
                    id='dlgChpasswd', title="Changing password for user %s" % self._edit)
                )

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            self._add = True
        if params[0] == 'edit':
            self._edit = self._users[int(params[1])]
        if params[0] == 'del':
            try:
                u = self._users[int(params[1])]
                self._rc.del_user(u)
                self.put_message('success', 'User deleted successfully')
            except Exception, e:
                self.app.log.error('Calendar user could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'User could not be deleted')

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmSetup':
            vaddr = True
            addr = vars.getvalue('addr', '')
            port = vars.getvalue('port', '')
            for site in apis.webapps(self.app).get_sites():
                if addr == site.addr and port == site.port:
                    vaddr = False
            if not addr or not port:
                self.put_message('err', 'Must choose an address and port!')
            elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
                self.put_message('err', 'Can\'t use the same port number as Genesis')
            elif not vaddr:
                self.put_message('err', 'This domain/subdomain and port conflicts with a website you have. '
                    'Change one of the two, or remove the site before continuing.')
            else:
                try:
                    self._rc.setup(addr, port)
                except Exception, e:
                    self.put_message('err', 'Setup failed: %s'%str(e))
        elif params[0] == 'dlgAddUser':
            acct = vars.getvalue('acct', '')
            passwd = vars.getvalue('passwd', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid username')
                elif acct in self._users:
                    self.put_message('err', 'You already have a user with this name')
                elif not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._rc.add_user(acct, passwd)
                        self.put_message('success', 'User added successfully')
                    except Exception, e:
                        self.app.log.error('Calendar user %s could not be added. Error: %s' % (acct,str(e)))
                        self.put_message('err', 'User could not be added')
            self._add = None
        if params[0] == 'dlgChpasswd':
            passwd = vars.getvalue('chpasswd', '')
            if vars.getvalue('action', '') == 'OK':
                if not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('chpasswdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._rc.edit_user(self._edit, passwd)
                        self.put_message('success', 'Password changed successfully')
                    except Exception, e:
                        self.app.log.error('Calendar password for %s could not be changed. Error: %s' % (self._edit,str(e)))
                        self.put_message('err', 'Password could not be changed')
            self._edit = None
