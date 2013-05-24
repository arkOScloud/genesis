from genesis.ui import *
from genesis.com import implements
from genesis.api import *
from genesis.utils import *

from backend import *


class UsersPlugin(CategoryPlugin):
    text = 'Users'
    iconfont = 'gen-users'
    folder = 'system'

    params = {
            'login': 'Login',
            'password': 'Password',
            'name': 'Name',
            'uid': 'UID',
            'home': 'Home directory',
            'adduser': 'New user login',
        }


    def on_init(self):
        self.backend = UsersBackend(self.app)
        self.users = self.backend.get_all_users()

    def reload_data(self):
        self.users = self.backend.get_all_users()

    def get_config(self):
        return self.app.get_config(self.backend)

    def on_session_start(self):
        self._tab = 0
        self._selected_user = ''
        self._editing = ''

    def get_ui(self):
        self.reload_data()
        ui = self.app.inflate('users:main')

        if self._editing != '':
            if self._editing in self.params:
                ui.find('dlgEdit').set('text', self.params[self._editing])
        else:
            ui.remove('dlgEdit')

        # Users
        t = ui.find('userlist')

        for u in self.users:
            if u.uid == 0 or u.uid >= 1000:
                t.append(UI.DTR(
                        UI.IconFont(iconfont='gen-user'),
                        UI.Label(text=u.login, bold=True),
                        UI.Label(text=u.uid, bold=True),
                        UI.Label(text=u.home),
                        UI.TipIcon(iconfont='gen-pencil-2', id='edit/'+u.login, text='Edit'),
                    ))

        if self._selected_user != '':
            u = self.backend.get_user(self._selected_user, self.users)

            ui.find('elogin').set('value', u.login)
            ui.find('deluser').set('warning', 'Delete user %s'%u.login)
            ui.find('ehome').set('value', u.home)
        else:
            ui.remove('dlgEditUser')

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
        if params[0] == 'deluser':
            self._tab = 0
            self.backend.del_user(self._selected_user)
            try:
                self.app.gconfig.remove_option('users', self._selected_user)
                self.app.gconfig.save()
            except:
                pass
            self._selected_user = ''

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
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
            self._editing = ''
        if params[0].startswith('e'):
            v = vars.getvalue('value', '')
            if params[0] == 'epassword':
                self.backend.change_user_password(self._selected_user, v)
                self.app.gconfig.set('users', self._selected_user, hashpw(v))
            elif params[0] == 'elogin':
                self.backend.change_user_param(self._selected_user, editing, v)
                pw = self.app.gconfig.get('users', self._selected_user, '')
                self.app.gconfig.remove_option('users', self._selected_user)
                self.app.gconfig.set('users', v, pw)
                self._selected_user = v
            elif params[0] in self.params:
                self.backend.change_user_param(self._selected_user, editing, v)
            self._editing = None
        if params[0] == 'dlgEditUser':
            self._selected_user = ''
