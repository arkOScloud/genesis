from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis import apis

from genesis.plugins.users.backend import UsersBackend

import os
import backend
import re


class SambaPlugin(apis.services.ServiceControlPlugin):
    text = 'Fileshares (Win)'
    iconfont = 'gen-upload-2'
    folder = 'servers'
    
    def on_session_start(self):
        self._tab = 0
        self._cfg = backend.SambaConfig(self.app)
        self._cfg.load()
        self._editing_share = None
        self._editing_user = None
        self._editing = None
        self._adding_user = False

    def get_main_ui(self):
        ui = self.app.inflate('samba:main')
        ui.find('tabs').set('active', self._tab)

        # Shares
        for h in self._cfg.get_shares():
            r = UI.DTR(
                UI.IconFont(iconfont='gen-folder'),
                UI.Label(text=h),
                UI.Label(text=self._cfg.shares[h]['path']),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-pencil-2',
                        text='Edit', id='editshare/' + h),
                    UI.TipIcon(
                        iconfont='gen-close',
                        text='Delete', id='delshare/' + h, warning='Are you sure you want to delete the %s share?'%h)
                ),
            )
            ui.append('shares', r)

        if not self._editing_share is None:
            if self._editing_share == '':
                ui.append('main', self.get_ui_edit_share())
            else:
                ui.append('main', self.get_ui_edit_share(
                    self._cfg.shares[self._editing_share]
                ))

        # Users
        for h in sorted(self._cfg.users.keys()):
            r = UI.DTR(
                UI.IconFont(iconfont='gen-user'),
                UI.Label(text=h),
                UI.HContainer(
                    #UI.TipIcon(iconfont='gen-pencil-2',
                    #    text='Edit', id='edituser/' + h),
                    UI.TipIcon(
                        iconfont='gen-close',
                        text='Delete', id='deluser/' + h, warning='Are you sure you want to delete %s from the Samba users list?'%h)
                ),
            )
            ui.append('users', r)

        #if not self._editing_user is None:
        #    if self._editing_user == '':
        #        ui.append('main', self.get_ui_edit_user())
        #    else:
        #        if not self._editing_user in self._cfg.users.keys():
        #            self.put_message('err', 'User not found')
        #            self._editing_user = None
        #        else:
        #            ui.append('main', self.get_ui_edit_user(
        #                self._cfg.users[self._editing_user]
        #            ))

        if not self._editing is None:
            ui.append('main', UI.InputBox(
                title=self._editing,
                value=self._cfg.users[self._editing_user][self._editing],
                id='dlgEdit'
            ))

        if self._adding_user:
            users = [UI.SelectOption(text=x.login, value=x.login) for x in UsersBackend(self.app).get_all_users() if x.uid >= 1000]
            if users:
                ui.append('main',
                    UI.DialogBox(
                        UI.FormLine(
                            UI.Select(*users, name='acct', id='acct'),
                            text='Username'
                        ),
                        UI.FormLine(
                            UI.EditPassword(id='passwd', value='Click to add password'),
                            text='Password'
                        ),
                        id='dlgAddUser')
                    )
            else:
                self.put_message('err', 'No non-root Unix users found')
    
        # Config
        ui.append('tab2', self.get_ui_general())
        
        return ui

    def get_ui_edit_share(self, s=None):
        if s is None or s == '':
            s = self._cfg.new_share()

        dlg = UI.DialogBox(
            UI.Container(
                UI.Formline(
                    UI.TextInput(name='name'),
                    text='Name', help='The name you will use to connect to your share'
                ) if self._editing_share == '' else None,
                UI.Formline(
                    UI.TextInput(name='path', value=s['path']),
                    text='Path', help='The path to the folder on the disk you want to share'
                ),
                UI.Formline(
                    *[UI.Checkbox(text=x, name='validusers[]', value=x, checked=True if x in s['valid users'] else False) \
                        for x in sorted(self._cfg.users.keys())],
                    text='Valid users', help='A list of Samba users that will be able to connect to this share'
                ) if self._cfg.users.keys() else None,
                UI.Formline(
                    UI.Checkbox(text='Yes', name='browseable', checked=s['browseable']=='yes'),
                    text='Browseable?', help='This share will show up in Windows Explorer/My Computer'
                ),
                UI.Formline(
                    UI.Checkbox(text='Yes', name='read only', checked=s['read only']=='yes'),
                    text='Read only?', help='Prevent anyone from editing or deleting files in this share'
                ),
                UI.Formline(
                    UI.Checkbox(text='Yes', name='guest ok', checked=s['guest ok']=='yes'),
                    text='Guest access?', help='Allow anyone (not just valid users) to connect to this share'
                ),
                UI.Formline(
                    UI.Checkbox(text='Yes', name='only guest', checked=s['only guest']=='yes'),
                    text='Force guest?', help='Only allow guests to connect (ignores the \'valid users\' field)'
                )
            ),
            id='dlgEditShare',
            title='Edit share'
        )
        return dlg

    #def get_ui_edit_user(self, u=None):
    #    t = UI.Container()
    #    for k in self._cfg.fields:
    #        if k in u.keys():
    #            t.append(
    #                UI.Formline(
    #                    UI.Label(text=u[k]),
    #                    UI.Button(design='mini',
    #                        text='Change', id='chuser/'+k) if k in self._cfg.editable else None,
    #                    text=k
    #                )
    #            )
    #
    #    dlg = UI.DialogBox(
    #        t,
    #        title='Edit user',
    #        id='dlgEditUser'
    #    )
    #    return dlg

    def get_ui_general(self):
        dlg = UI.FormBox(
            UI.Formline(
                UI.TextInput(name='server string', value=self._cfg.general['server string']),
                text='Machine description',
            ),
            UI.Formline(
                UI.TextInput(name='workgroup', value=self._cfg.general['workgroup']),
                text='Workgroup',
            ),
            UI.Formline(
                UI.TextInput(name='interfaces', value=self._cfg.general['interfaces']),
                text='Listen on interfaces', help='Space-separated list. Can be interfaces (eth0), IP addresses or IP/mask pairs'
            ),
            id='frmGeneral'
        )
        return dlg

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'restart':
            backend.restart()
        if params[0] == 'editshare':
            self._editing_share = params[1]
            self._tab = 0
        if params[0] == 'delshare':
            if params[1] in self._cfg.shares.keys():
                del self._cfg.shares[params[1]]
            self._cfg.save()
            self._tab = 0
        if params[0] == 'newshare':
            self._editing_share = ''
            self._tab = 0
        #if params[0] == 'edituser':
        #    self._editing_user = params[1]
        #    self._tab = 1
        if params[0] == 'newuser':
            self._adding_user = True
            self._tab = 1
        if params[0] == 'deluser':
            self._cfg.del_user(params[1])
            self._cfg.load()
            self._tab = 1
        if params[0] == 'chuser':
            self._tab = 1
            self._editing = params[1]

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditShare':
            if vars.getvalue('action', '') == 'OK':
                if vars.has_key('name') and not vars.getvalue('name', ''):
                    self.put_message('err', 'Must choose a valid name for this share')
                elif not vars.getvalue('path', '') or not os.path.isdir(vars.getvalue('path')):
                    self.put_message('err', 'Must choose a valid path on disk')
                else:
                    es = self._editing_share
                    if es == '':
                        es = vars.getvalue('name', 'new')
                        self._cfg.shares[es] = self._cfg.new_share()

                    validusers = []
                    for i in range(0, len(sorted(self._cfg.users.keys()))):
                        try:
                            if vars.getvalue('validusers[]')[i] == '1':
                                validusers.append(sorted(self._cfg.users.keys())[i])
                        except TypeError:
                            pass

                    self._cfg.set_param_from_vars(es, 'path', vars)
                    if validusers:
                        self._cfg.set_param(es, 'valid users', ' '.join(validusers))
                    self._cfg.set_param_from_vars_yn(es, 'browseable', vars)
                    self._cfg.set_param_from_vars_yn(es, 'read only', vars)
                    self._cfg.set_param_from_vars_yn(es, 'guest ok', vars)
                    self._cfg.set_param_from_vars_yn(es, 'only guest', vars)
                    self._cfg.save()
            self._editing_share = None
        if params[0] == 'frmGeneral':
            if vars.getvalue('action', '') == 'OK':
                self._cfg.set_param_from_vars('general', 'server string', vars)
                self._cfg.set_param_from_vars('general', 'workgroup', vars)
                self._cfg.set_param_from_vars('general', 'interfaces', vars)
                self._cfg.save()
            self._tab = 2

        #if params[0] == 'dlgEditUser':
        #    self._editing_user = None

        if params[0] == 'dlgAddUser':
            acct = vars.getvalue('acct', '')
            passwd = vars.getvalue('passwd', '')
            if vars.getvalue('action', '') == 'OK':
                m = re.match('([-0-9a-zA-Z.+_]+)', acct)
                if not acct or not m:
                    self.put_message('err', 'Must choose a valid username')
                elif acct in self._cfg.users.keys():
                    self.put_message('err', 'You already have a user with this name')
                elif not passwd:
                    self.put_message('err', 'Must choose a password')
                elif passwd != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                else:
                    self._cfg.add_user(acct, passwd)
                    self._cfg.load()
            self._adding_user = False

        if params[0] == 'dlgEdit':
            if vars.getvalue('action', '') == 'OK':
                self._cfg.modify_user(self._editing_user, self._editing, vars.getvalue('value', ''))
                self._cfg.load()
            self._editing = None
