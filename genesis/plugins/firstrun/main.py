from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis.plugmgr import RepositoryManager

from genesis.plugins.users.backend import *

class FirstRun(CategoryPlugin, URLHandler):
    text = 'First run wizard'
    icon = None
    folder = None

    def on_session_start(self):
        self._step = 1

    def get_ui(self):
        ui = self.app.inflate('firstrun:main')
        step = self.app.inflate('firstrun:step%i'%self._step)
        ui.append('content', step)

        if self._step == 2:
            self._mgr = RepositoryManager(self.app.config)
            self._mgr.update_list()

            lst = self._mgr.available

            for k in sorted(lst, key=lambda x:x.name):
                row = self.app.inflate('firstrun:item')
                row.find('name').set('text', k.name)
                row.find('desc').set('text', k.description)
                row.find('icon').set('file', k.icon)
                row.find('version').set('text', k.version)
                row.find('author').set('text', k.author)
                row.find('author').set('url', k.homepage)

                req = k.str_req()

                row.find('check').set('name', 'install-'+k.id)
                if req != '':
                    row.append('reqs', UI.HelpIcon(text=req))

                ui.append('list', row)

        return ui

    @event('form/submit')
    def on_event(self, event, params, vars=None):
        if params[0] == 'frmChangePassword':
            username = vars.getvalue('login', '')
            password = vars.getvalue('password', '')
            if username == '' or password == '':
                self.put_message('err', 'Enter valid login and password')
            else:
                # add Unix user
                users = self.backend.get_all_users()
                for u in users:
                    if u.login == username:
                        self.put_message('err', 'Duplicate name, please choose another')
                        self._editing = ''
                        return
                self.backend.add_user(username)
                self.backend.change_user_password(username, password)

                # add user to Genesis config
                self.app.gconfig.remove_option('users', 'admin')
                self.app.gconfig.set('users', username, hashpw(password))
                self.app.gconfig.save()
                self._step = 2
        if params[0] == 'frmPlugins':
            lst = self._mgr.available

            for k in lst:
                if vars.getvalue('install-'+k.id, '0') == '1':
                    try:
                        self._mgr.install(k.id)
                    except:
                        pass
            ComponentManager.get().rescan()
            ConfManager.get().rescan();

            self.app.gconfig.set('genesis', 'firstrun', 'no')
            self.app.gconfig.save()
            self.put_message('info', 'Setup complete')
            self._step = 3
