import re

from genesis.ui import *
from genesis.com import implements
from genesis.api import *
from genesis.utils import *

from backend import *


class UsersPlugin(CategoryPlugin):
    text = 'Users'
    iconfont = 'gen-users'
    folder = None

    params = {
            'login': 'Login',
            'password': 'Password',
            'name': 'Name',
            'uid': 'UID',
            'gid': 'GID',
            'home': 'Home directory',
            'shell': 'Shell',
            'groups': 'Groups',
            'adduser': 'New user login',
            'addgrp': 'New group name',
            'addtogroup': 'Add to group',
            'delfromgroup': 'Delete from group',
        }


    def on_init(self):
        self.backend = UsersBackend(self.app)
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

    def reload_data(self):
        self.users = self.backend.get_all_users()
        self.groups = self.backend.get_all_groups()
        self.backend.map_groups(self.users, self.groups)

    def get_config(self):
        return self.app.get_config(self.backend)

    def on_session_start(self):
        self._tab = 0
        self._selected_user = ''
        self._selected_group = ''
        self._editing = ''

    def get_ui(self):
        self.reload_data()
        ui = self.app.inflate('users:main')
        ui.find('tabs').set('active', self._tab)

        if self._editing == 'deluser':
            u = self.backend.get_user(self._selected_user, self.users)
            ui.find('dlgConfirmDelete').set('text', 
                'Do you want to delete user data (stored at %s) for %s?' % (u.home, u.login))
            ui.remove('dlgEdit')
        elif self._editing != '' and self._editing in self.params:
            ui.find('dlgEdit').set('text', self.params[self._editing])
            ui.remove('dlgConfirmDelete')
        elif self._editing != '':
            ui.find('dlgEdit').set('text', self.gparams[self._editing])
        else:
            ui.remove('dlgEdit')
            ui.remove('dlgConfirmDelete')

        # Users
        t = ui.find('userlist')
        s = ui.find('sysuserlist')

        for u in self.users:
            if u.uid == 0 or u.uid >= 1000:
                t.append(UI.DTR(
                        UI.IconFont(iconfont='gen-user'),
                        UI.Label(text=u.login, bold=True),
                        UI.Label(text=u.uid, bold=True),
                        UI.Label(text=u.home),
                        UI.TipIcon(iconfont='gen-pencil-2', id='edit/'+u.login, text='Edit'),
                    ))
            else:
                s.append(UI.DTR(
                        UI.IconFont(iconfont='gen-user'),
                        UI.Label(text=u.login, bold=True),
                        UI.Label(text=u.uid, bold=(u.uid>=1000)),
                        UI.Label(text=u.home),
                        UI.Label(text=u.shell),
                        UI.TipIcon(iconfont='gen-pencil-2', id='edit/'+u.login, text='Edit'),
                    ))

        if self._selected_user != '' and self._editing != 'deluser':
            u = self.backend.get_user(self._selected_user, self.users)
            self.backend.map_groups([u], self.backend.get_all_groups())
            ui.find('login').set('value', u.login)
            ui.find('home').set('text', u.home)
            ui.find('euid').set('value', str(u.uid))
            ui.find('egid').set('value', str(u.gid))
            ui.find('eshell').set('value', u.shell)
            ui.find('lblugroups').set('text', ', '.join(u.groups))
        else:
            ui.remove('dlgEditUser')

        # Groups
        t = ui.find('grouplist')

        for u in self.groups:
            t.append(UI.DTR(
                    UI.IconFont(iconfont='gen-users'),
                    UI.Label(text=u.name, bold=True),
                    UI.Label(text=u.gid, bold=(u.gid>=1000)),
                    UI.Label(text=', '.join(u.users)),
                    UI.TipIcon(iconfont='gen-pencil-2', id='gedit/'+u.name, text='Edit'),
                ))

        if self._selected_group != '':
            u = self.backend.get_group(self._selected_group, self.groups)
            g = ', '.join(u.users)

            ui.find('ename').set('value', u.name)
            ui.find('delgroup').set('warning', 'Delete group %s'%u.name)
            ui.find('eggid').set('value', str(u.gid))
            ui.find('lblgusers').set('text', g)
        else:
            ui.remove('dlgEditGroup')

        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'edit':
            self._tab = 0
            self._selected_user = params[1]
        if params[0] == 'gedit':
            self._tab = 1
            self._selected_group = params[1]
        if params[0].startswith('ch'):
            self._tab = 0
            self._editing = params[0][2:]
        if params[0] == 'adduser':
            self._tab = 0
            self._editing = 'adduser'
        if params[0] == 'addgrp':
            self._tab = 1
            self._editing = 'addgrp'
        if params[0] == 'deluser':
            self._editing = 'deluser'
        if params[0] == 'delgroup':
            self._tab = 1
            self.backend.del_group(self._selected_group)
            self._selected_group = ''

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
                    if re.search('[A-Z]|\.|:|[ ]|-$', v):
                        self.put_message('err', 'Username must not contain capital letters, dots, colons, spaces, or end with a hyphen')
                        self._editing = ''
                        return
                    self.reload_data()
                    for u in self.users:
                        if u.login == v:
                            self.put_message('err', 'Duplicate name')
                            self._editing = ''
                            return
                    self.app.gconfig.set('users', v, '')
                    self.app.gconfig.save()
                    self.backend.add_user(v)
                    self._selected_user = v
                    self.put_message("success", "User added. Don't forget to add a password if you want to be able to login with this user!")
                elif self._editing == 'addgrp':
                    self.reload_data()
                    for u in self.groups:
                        if u.name == v:
                            self.put_message('err', 'Duplicate name')
                            self._editing = ''
                            return
                    self.backend.add_group(v)
                    self._selected_group = v
                elif self._editing == 'addtogroup':
                    self.backend.add_to_group(self._selected_user, v)
                elif self._editing == 'delfromgroup':
                    self.backend.remove_from_group(self._selected_user, v)
            self._editing = ''
        if params[0] == 'dlgEditUser':
            if vars.getvalue('passwd', '') != '':
                v = vars.getvalue('passwd')
                if v != vars.getvalue('passwdb',''):
                    self.put_message('err', 'Passwords must match')
                    self._selected_user = ''
                else:
                    self.backend.change_user_password(self._selected_user, v)
                    self.app.gconfig.set('users', self._selected_user, hashpw(v))
                    self.app.gconfig.save()
            if vars.getvalue('login', '') != '' and vars.getvalue('login', '') != self._selected_user:
                v = vars.getvalue('login')
                for u in self.users:
                    if u.login == v:
                        self.put_message('err', 'Duplicate name')
                        self._selected_user = ''
                        return
                if re.search('[A-Z]|\.|:|[ ]|-$', v):
                    self.put_message('err', 'Username must not contain capital letters, dots, colons, spaces, or end with a hyphen')
                    self._selected_user = ''
                else:
                    self.backend.change_user_param(self._selected_user, 'login', v)
                    pw = self.app.gconfig.get('users', self._selected_user, '')
                    self.app.gconfig.remove_option('users', self._selected_user)
                    self.app.gconfig.set('users', v, pw)
                    self._selected_user = v
                    self.app.gconfig.save()
                    self._editing = ''
            self._selected_user = ''
        if params[0] == 'dlgConfirmDelete':
            self._tab = 0
            answer = vars.getvalue('action', '')
            if answer == 'Confirm':
                self.backend.del_user_with_home(self._selected_user)
            elif answer == 'Reject':
                self.backend.del_user(self._selected_user)
            if answer != 'Cancel':
                try:
                    self.app.gconfig.remove_option('users', self._selected_user)
                    self.app.gconfig.save()
                except:
                    pass
            self._selected_user = ''
            self._editing = ''
