import re

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.databases.utils import DBAuthFail, DBConnFail

import backend

class MailPlugin(apis.services.ServiceControlPlugin):
    text = 'Mailserver'
    iconfont = 'gen-envelop'
    folder = 'servers'

    def on_session_start(self):
        self._edit = None
        self._addbox = None
        self._addalias = None
        self._adddom = None
        self._list = None
        self._aliases, self._boxes = [], []
        self._config = backend.MailConfig(self.app)
        self._mc = backend.MailControl(self.app)
        self._config.load()

    def on_init(self):
        try:
            self._domains = self._mc.list_domains()
        except DBConnFail:
            pass

    def get_main_ui(self):
        ui = self.app.inflate('email:main')

        if not apis.databases(self.app).get_interface('MariaDB').checkpwstat():
            self.put_message('err', 'MariaDB does not have a root password set. '
                'Please add this via the Databases screen.')
            return ui
        elif not apis.databases(self.app).get_dbconn('MariaDB'):
            ui.append('main', UI.InputBox(id='dlgAuth', 
                text='Enter the database password for MariaDB', 
                password=True))
            return ui

        is_setup = self._mc.is_setup()
        if self.app.get_config(self._mc).reinitialize \
        or not is_setup:
            if not is_setup:
                self.put_message('err', 'Your mailserver does not appear to be properly configured. Please rerun this setup.')
            return UI.Btn(iconfont="gen-cog", text="Setup Mailserver", id="setup")

        t = ui.find('list')
        for x in self._domains:
            t.append(UI.DTR(
                UI.Iconfont(iconfont='gen-code'),
                UI.Label(text=x),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-pencil', id='list/'+str(self._domains.index(x)), text='Show Boxes/Aliases'),
                    UI.TipIcon(iconfont='gen-cancel-circle', id='deldom/'+str(self._domains.index(x)), text='Delete Domain',
                        warning='Are you sure you want to delete mail domain %s?'%x)
                ),
            ))

        if self._addbox:
            doms = [UI.SelectOption(text=x, value=x) for x in self._domains]
            if doms:
                ui.append('main',
                    UI.DialogBox(
                        UI.FormLine(
                            UI.TextInput(name='acct', id='acct'),
                            text='Account Name', help="The \'name\' in name@example.com"
                        ),
                        UI.FormLine(
                            UI.Select(*doms if doms else 'None', id='dom', name='dom'),
                            text='Domain'
                        ),
                        UI.FormLine(
                            UI.EditPassword(id='passwd', value='Click to add password'),
                            text='Password'
                        ),
                        UI.FormLine(
                            UI.TextInput(name='fullname', id='fullname'),
                            text='Full Name'
                        ),
                        UI.FormLine(
                            UI.TextInput(name='quota', id='quota'),
                            text='Quota (in MB)', help='Enter 0 for unlimited'
                        ),
                        id='dlgAddBox')
                    )
            else:
                self.put_message('err', 'You must add a domain first!')
                self._addbox = None

        if self._addalias:
            doms = [UI.SelectOption(text=x, value=x) for x in self._domains]
            if doms:
                ui.append('main',
                    UI.DialogBox(
                        UI.FormLine(
                            UI.TextInput(name='acct', id='acct'),
                            text='Account Name', help="The \'name\' in name@example.com"
                        ),
                        UI.FormLine(
                            UI.Select(*doms if doms else 'None', id='dom', name='dom'),
                            text='Domain'
                        ),
                        UI.FormLine(
                            UI.TextInput(name='forward', id='forward'),
                            text='Points to', help="A full email address to forward messages to"
                        ),
                        id='dlgAddAlias')
                    )
            else:
                self.put_message('err', 'You must add a domain first!')
                self._addalias = None

        if self._adddom:
            ui.append('main',
                UI.InputBox(id='dlgAddDom', text='Enter domain name to add'))

        if self._edit:
            ui.append('main',
                UI.DialogBox(
                    UI.FormLine(
                        UI.Label(text=self._edit['username']+'@'+self._edit['domain']),
                        text="Editing mailbox for"
                    ),
                    UI.FormLine(
                        UI.TextInput(name='quota', id='quota', value=self._edit['quota']),
                        text='Quota (in MB)', help="Enter 0 for unlimited"
                    ),
                    UI.FormLine(
                        UI.EditPassword(id='chpasswd', value='Click to change password'),
                        text='Password'
                    ),
                    id='dlgEdit')
                )

        if self._list:
            dui = self.app.inflate('email:list')
            t = dui.find('ulist')
            self._boxes = []
            for x in self._mc.list_mailboxes(self._list):
                self._boxes.append(x)
                t.append(UI.DTR(
                    UI.Iconfont(iconfont='gen-user'),
                    UI.Label(text=x['username']),
                    UI.Label(text=x['name']),
                    UI.Label(text=x['quota']+' MB' if x['quota'] != '0' else 'Unlimited'),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-key', id='edit/'+str(self._boxes.index(x)), text='Edit Mailbox'),
                        UI.TipIcon(iconfont='gen-cancel-circle', id='delbox/'+str(self._boxes.index(x)), text='Delete Mailbox',
                            warning='Are you sure you want to delete mailbox %s@%s?'%(x['username'],x['domain']))
                    ),
                ))
            t = dui.find('alist')
            self._aliases = []
            for x in self._mc.list_aliases(self._list):
                self._aliases.append(x)
                t.append(UI.DTR(
                    UI.Iconfont(iconfont='gen-link'),
                    UI.Label(text=x['address']),
                    UI.Label(text=x['forward']),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-cancel-circle', id='delal/'+str(self._aliases.index(x)), text='Delete Mailbox',
                            warning='Are you sure you want to delete alias %s, pointing at %s?'%(x['address'],x['forward']))
                    ),
                ))
            ui.append('main',
                UI.DialogBox(dui, id='dlgList')
            )

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'setup':
            self._mc.initial_setup()
        elif params[0] == 'add':
            self._addbox = True
        elif params[0] == 'addalias':
            self._addalias = True
        elif params[0] == 'adddom':
            self._adddom = True
        elif params[0] == 'list':
            self._list = self._domains[int(params[1])]
        elif params[0] == 'edit':
            self._list = None
            b = self._boxes[int(params[1])]
            self._boxes = []
            self._edit = b
        elif params[0] == 'delbox':
            try:
                b = self._boxes[int(params[1])]
                self._boxes = []
                self._mc.del_mailbox(b['username'], b['domain'])
                self.put_message('info', 'Mailbox deleted successfully')
            except Exception, e:
                self.app.log.error('Mailbox could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'Mailbox could not be deleted')
        elif params[0] == 'delal':
            try:
                a = self._aliases[int(params[1])]
                self._aliases = []
                self._mc.del_alias(a['address'], a['forward'])
                self.put_message('info', 'Alias deleted successfully')
            except Exception, e:
                self.app.log.error('Alias could not be deleted. Error: %s' % str(e))
                self.put_message('err', 'Alias could not be deleted')
        elif params[0] == 'deldom':
            for x in self._boxes + self._aliases:
                if x['domain'] == self._domains[int(params[1])]:
                    self.put_message('err', 'You still have mailboxes or aliases attached to this domain. Remove them before deleting the domain!')
                    break
            else:
                self._mc.del_domain(self._domains[int(params[1])])
                self.put_message('info', 'Domain deleted')

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddBox':
            acct = vars.getvalue('acct', '')
            dom = vars.getvalue('dom', '')
            passwd = vars.getvalue('passwd', '')
            fullname = vars.getvalue('fullname', '')
            quota = vars.getvalue('quota', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid mailbox name')
                elif acct in [x['username'] for x in self._mc.list_mailboxes(dom)]:
                    self.put_message('err', 'You already have a mailbox with this name on this domain')
                elif not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._mc.add_mailbox(acct, dom, passwd, fullname, quota)
                        self.put_message('info', 'Mailbox added successfully')
                    except Exception, e:
                        self.app.log.error('Mailbox %s@%s could not be added. Error: %s' % (acct,dom,str(e)))
                        self.put_message('err', 'Mailbox could not be added')
            self._addbox = None
        elif params[0] == 'dlgAddAlias':
            acct = vars.getvalue('acct', '')
            dom = vars.getvalue('dom', '')
            forward = vars.getvalue('forward', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid alias name')
                elif (acct+'@'+dom, forward) in [(x['address'], x['forward']) for x in self._mc.list_aliases(dom)]:
                    self.put_message('err', 'This alias has already been created')
                else:
                    try:
                        self._mc.add_alias(acct, dom, forward)
                        self.put_message('info', 'Alias added successfully')
                    except Exception, e:
                        self.app.log.error('Alias from %s@%s to %s could not be added. Error: %s' % (acct,dom,forward,str(e)))
                        self.put_message('err', 'Alias could not be added')
            self._addalias = None
        elif params[0] == 'dlgAddDom':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if not v or not re.match('([-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4})', v):
                    self.put_message('err', 'Must enter a valid domain to add')
                elif v in self._domains:
                    self.put_message('err', 'You have already added this domain!')
                else:
                    try:
                        self._mc.add_domain(v)
                        self.put_message('info', 'Domain added successfully')
                    except Exception, e:
                        self.app.log.error('Domain %s could not be added. Error: %s' % (v,str(e)))
                        self.put_message('err', 'Domain could not be added')
            self._adddom = None
        if params[0] == 'dlgList':
            self._list = None
        if params[0] == 'dlgEdit':
            quota = vars.getvalue('quota', '')
            passwd = vars.getvalue('chpasswd', '')
            if vars.getvalue('action', '') == 'OK':
                if passwd and passwd != vars.getvalue('chpasswdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._mc.edit(self._edit['username'], self._edit['domain'], 
                            quota, passwd)
                        self.put_message('info', 'Mailbox edited successfully')
                    except Exception, e:
                        self.app.log.error('Mailbox %s@%s could not be edited. Error: %s' % (self._edit['username'],self._edit['domain'],str(e)))
                        self.put_message('err', 'Mailbox could not be edited')
            self._edit = None
        if params[0].startswith('dlgAuth'):
            if vars.getvalue('action', '') == 'OK':
                login = vars.getvalue('value', '')
                try:
                    apis.databases(self.app).get_interface('MariaDB').connect(
                        store=self.app.session['dbconns'],
                        passwd=login)
                except DBAuthFail, e:
                    self.put_message('err', str(e))
