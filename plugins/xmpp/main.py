import re

from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class XMPPPlugin(apis.services.ServiceControlPlugin):
    text = 'Chat (XMPP)'
    iconfont = 'gen-bubbles'
    folder = 'servers'

    def on_session_start(self):
        self._chpasswd = None
        self._adduser = None
        self._config = backend.XMPPConfig(self.app)
        self._uc = backend.XMPPUserControl()
        self._config.load()

    def on_init(self):
        self._users = self._uc.list_users()

    def get_main_ui(self):
        ui = self.app.inflate('xmpp:main')

        t = ui.find('list')
        for u in self._users:
            t.append(UI.DTR(
                    UI.Iconfont(iconfont='gen-user'),
                    UI.Label(text=u[0]),
                    UI.Label(text=u[1]),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-key', id='edit/'+str(self._users.index(u)), text='Change Password'),
                        UI.TipIcon(iconfont='gen-cancel-circle', id='del/'+str(self._users.index(u)), text='Delete', warning='Are you sure you want to delete XMPP account %s@%s?'%(u[0], u[1]))
                    ),
                ))

        if self._adduser:
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

        if self._chpasswd:
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
            self._adduser = True
        elif params[0] == 'edit':
            self._chpasswd = self._users[int(params[1])]
        elif params[0] == 'del':
            try:
                u = self._users[int(params[1])]
                self._uc.del_user(u[0], u[1])
                self.put_message('info', 'User deleted successfully')
            except Exception, e:
                self.app.log.error('XMPP user could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'User could not be deleted')

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddUser':
            acct = vars.getvalue('acct', '')
            passwd = vars.getvalue('passwd', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)@([-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4})', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid JID username (format: test@example.com)')
                elif not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    user, dom = m.group(1,2)
                    try:
                        self._uc.add_user(user, dom, passwd)
                        self.put_message('info', 'User added successfully')
                    except Exception, e:
                        self.app.log.error('XMPP user %s@%s could not be added. Error: %s' % (user,dom,str(e)))
                        self.put_message('err', 'User could not be added')
            self._adduser = None
        elif params[0] == 'dlgChpasswd':
            passwd = vars.getvalue('chpasswd', '')
            if vars.getvalue('action', '') == 'OK':
                if not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('chpasswdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._uc.chpasswd(self._chpasswd[0], 
                            self._chpasswd[1], passwd)
                        self.put_message('info', 'Password changed successfully')
                    except Exception, e:
                        self.app.log.error('XMPP password for %s@%s could not be changed. Error: %s' % (self._chpasswd[0],self._chpasswd[1],str(e)))
                        self.put_message('err', 'Password could not be changed')
            self._chpasswd = None
