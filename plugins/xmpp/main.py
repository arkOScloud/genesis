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
        self._domains = self._config.domains()

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

        t = ui.find('dlist')
        for x in self._domains:
            if not self._config.config['_VirtualHost_'+x].has_key('enabled'):
                self._config.config['_VirtualHost_'+x]['enabled'] = False
            t.append(UI.DTR(
                    UI.Iconfont(iconfont='gen-code'),
                    UI.Label(text=x),
                    UI.Label(text='Enabled' if self._config.config['_VirtualHost_'+x]['enabled'] else 'Disabled'),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-pencil', id='editdom/'+str(self._domains.index(x)), text='Edit Domain'),
                        UI.TipIcon(iconfont='gen-%s'%('link' if not self._config.config['_VirtualHost_'+x]['enabled'] else 'link-2'), 
                            id='togdom/'+str(self._domains.index(x)), text=('Disable' if self._config.config['_VirtualHost_'+x]['enabled'] else 'Enable')),
                        UI.TipIcon(iconfont='gen-cancel-circle', id='deldom/'+str(self._domains.index(x)), text='Delete Domain',
                            warning='Are you sure you want to delete XMPP domain %s?'%x),
                    ),
                ))

        if self._adduser:
            doms = [UI.SelectOption(text=x, value=x) for x in self._domains]
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.TextInput(name='acct', id='acct'),
                        text='Username'
                    ),
                    UI.FormLine(
                        UI.Select(*doms if doms else 'None', id='dom', name='dom'),
                        text='Domain'
                    ),
                    UI.FormLine(
                        UI.EditPassword(id='passwd', value='Click to add password'),
                        text='Password'
                    ),
                    id='dlgAddUser')
                )

        if self._adddom:
            ui.append('main',
                UI.InputBox(id='dlgAddDom', text='Enter domain name to add'))

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
        elif params[0] == 'adddom':
            self._adddom = True
        elif params[0] == 'edit':
            self._chpasswd = self._users[int(params[1])]
        elif params[0] == 'togdom':
            self._config.config['_VirtualHost_%s'%self._domains[int(params[1])]]['enabled'] = True \
            if self._config.config['_VirtualHost_%s'%self._domains[int(params[1])]]['enabled'] == False \
            else False
            self._config.save()
        elif params[0] == 'del':
            try:
                u = self._users[int(params[1])]
                self._uc.del_user(u[0], u[1])
                self.put_message('info', 'User deleted successfully')
            except Exception, e:
                self.app.log.error('XMPP user could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'User could not be deleted')
        elif params[0] == 'deldom':
            candel = True
            for x in self._users:
                if x[1] == self._domains[int(params[1])]:
                    self.put_message('err', 'You still have user accounts attached to this domain. Remove them before deleting the domain!')
                    candel = False
            if candel:
                del self._config.config['_VirtualHost_%s'%self._domains[int(params[1])]]
                self.put_message('info', 'Domain deleted')
                self._config.save()

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddUser':
            acct = vars.getvalue('acct', '')
            dom = vars.getvalue('dom', '')
            passwd = vars.getvalue('passwd', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid username')
                elif (acct, dom) in self._users:
                    self.put_message('err', 'You already have a user with this name on this domain')
                elif not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._uc.add_user(acct, dom, passwd)
                        self.put_message('info', 'User added successfully')
                    except Exception, e:
                        self.app.log.error('XMPP user %s@%s could not be added. Error: %s' % (acct,dom,str(e)))
                        self.put_message('err', 'User could not be added')
            self._adduser = None
        elif params[0] == 'dlgAddDom':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if not v or not re.match('([-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4})', v):
                    self.put_message('err', 'Must enter a valid domain to add')
                elif v in self._domains:
                    self.put_message('err', 'You have already added this domain!')
                else:
                    self._config.set('_VirtualHost_%s'%v, {'enabled': False})
                    self._config.save()
                    self.put_message('info', 'Domain added successfully')
            self._adddom = None
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
