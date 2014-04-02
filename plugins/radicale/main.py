import re

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager

import backend

class RadicalePlugin(CategoryPlugin):
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
        self._users = self._rc.list_users()
        self.site = filter(lambda x: x.name=='radicale', self._wa.get_sites())
        if self.site:
            self.site = self.site[0]
        else:
            self.site = None

    def get_ui(self):
        is_installed = self._rc.is_installed()
        if not self.app.get_config(self._config).first_run_complete \
        or not is_installed:
            ui = self.app.inflate('radicale:setup')
            ui.find('addr').set('value', self.app.get_backend(IHostnameManager).gethostname())
            if not is_installed:
                self.put_message('err', 'Your Calendar/Contacts server does not appear to be properly configured. Please rerun this setup.')
            return ui
        ui = self.app.inflate('radicale:main')

        ui.find('rinfo').append(
            UI.Label(size='1', bold=True,
                text='Your Calendar/Contacts server is listening at http%s://%s%s'%('s' if self.site.ssl else '', self.site.addr, ':'+self.site.port if self.site.port not in ['80', '443'] else ''))
            )

        t = ui.find('list')
        for u in self._users:
            t.append(UI.DTR(
                    UI.Iconfont(iconfont='gen-user'),
                    UI.Label(text=u),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-key', id='edit/'+str(self._users.index(u)), text='Change Password'),
                        UI.TipIcon(iconfont='gen-cancel-circle', id='del/'+str(self._users.index(u)), text='Delete', warning='Are you sure you want to delete calendar user %s?'%u)
                    ),
                ))

        if self._add:
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.TextInput(name='acct', id='acct'),
                        text='Username'
                    ),
                    UI.FormLine(
                        UI.EditPassword(id='passwd', value='Click to add password'),
                        text='Password'
                    ),
                    id='dlgAddUser')
                )

        if self._edit:
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.EditPassword(id='chpasswd', value='Click to change password'),
                        text='Password'
                    ),
                    id='dlgChpasswd')
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
                self.put_message('info', 'User deleted successfully')
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
                        self.put_message('info', 'User added successfully')
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
                        self.put_message('info', 'Password changed successfully')
                    except Exception, e:
                        self.app.log.error('Calendar password for %s could not be changed. Error: %s' % (self._edit,str(e)))
                        self.put_message('err', 'Password could not be changed')
            self._edit = None
