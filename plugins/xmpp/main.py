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

        for u in self._users:
            ui.append('main', UI.TblBtn(
                id='edit/'+str(self._users.index(u)),
                icon="gen-user",
                name=u[0],
                subtext=u[1]
            ))

        for x in self._domains:
            if not self._config.config['_VirtualHost_'+x].has_key('enabled'):
                self._config.config['_VirtualHost_'+x]['enabled'] = False
            ui.append('dlist', UI.TblBtn(
                UI.HContainer(
                    #UI.TipIcon(iconfont='gen-pencil', id='editdom/'+str(self._domains.index(x)), text='Edit Domain'),
                    UI.TipIcon(iconfont='gen-cancel-circle', id='deldom/'+str(self._domains.index(x)), text='Delete Domain',
                        warning='Are you sure you want to delete XMPP domain %s?'%x),
                ),
                id='togdom/'+str(self._domains.index(x)),
                icon="gen-code",
                name=x,
                subtext='Enabled' if self._config.config['_VirtualHost_'+x]['enabled'] else 'Disabled'
            ))

        ui.find('allow_registration').set('checked', True if self._config.config['allow_registration'] else False)
        ui.find('c2s_require_encryption').set('checked', True if self._config.config['c2s_require_encryption'] else False)
        ui.find('s2s_secure_auth').set('checked', True if self._config.config['s2s_secure_auth'] else False)

        if self._adduser:
            doms = [UI.SelectOption(text=x, value=x) for x in self._domains]
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.TextInput(name='acct', id='acct'),
                        text='Username'
                    ),
                    UI.FormLine(
                        UI.SelectInput(*doms if doms else 'None', id='dom', name='dom'),
                        text='Domain'
                    ),
                    UI.Formline(UI.TextInput(id='passwd', name="passwd", password=True, verify="password", verifywith="passwd"),
                        text="Password", feedback="gen-lock", iid="passwd"
                    ),
                    UI.Formline(UI.TextInput(id='passwdb', name="passwdb", password=True, verify="password", verifywith="passwd"),
                        text="Confirm password", feedback="gen-lock", iid="passwdb"
                    ),
                    id='dlgAddUser', title="Adding user")
                )

        if self._adddom:
            ui.append('main',
                UI.InputBox(id='dlgAddDom', text='Enter domain name to add'))

        if self._chpasswd:
            ui.append('main',
                UI.DialogBox(
                    UI.Formline(UI.TextInput(id='chpasswd', name="chpasswd", password=True, verify="password", verifywith="chpasswd"),
                        text="Password", feedback="gen-lock", iid="chpasswd"
                    ),
                    UI.Formline(UI.TextInput(id='chpasswdb', name="chpasswdb", password=True, verify="password", verifywith="chpasswd"),
                        text="Confirm password", feedback="gen-lock", iid="chpasswdb"
                    ),
                    id='dlgChpasswd', title="Changing password for %s" % self._chpasswd[0],
                    miscbtn="Delete", miscbtnid='del/'+str(self._users.index(u)), miscbtnstyle="danger",
                    miscbtnwarn='Are you sure you want to delete XMPP account %s@%s?'%(u[0], u[1]))
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
                self.put_message('success', 'User deleted successfully')
            except Exception, e:
                self.app.log.error('XMPP user could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'User could not be deleted')
            self._chpasswd = None
        elif params[0] == 'deldom':
            candel = True
            for x in self._users:
                if x[1] == self._domains[int(params[1])]:
                    self.put_message('err', 'You still have user accounts attached to this domain. Remove them before deleting the domain!')
                    candel = False
            if candel:
                del self._config.config['_VirtualHost_%s'%self._domains[int(params[1])]]
                self.put_message('success', 'Domain deleted')
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
                        self.put_message('success', 'User added successfully')
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
                    self.put_message('success', 'Domain added successfully')
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
                        self.put_message('success', 'Password changed successfully')
                    except Exception, e:
                        self.app.log.error('XMPP password for %s@%s could not be changed. Error: %s' % (self._chpasswd[0],self._chpasswd[1],str(e)))
                        self.put_message('err', 'Password could not be changed')
            self._chpasswd = None
        elif params[0] == 'frmOptions':
            if vars.getvalue('action', '') == 'OK':
                self._config.config['allow_registration'] = True if vars.getvalue('allow_registration', '') == '1' else False
                self._config.config['c2s_require_encryption'] = True if vars.getvalue('c2s_require_encryption', '') == '1' else False
                self._config.config['s2s_secure_auth'] = True if vars.getvalue('s2s_secure_auth', '') == '1' else False
                self._config.save()
                self.put_message('success', 'Settings saved')
