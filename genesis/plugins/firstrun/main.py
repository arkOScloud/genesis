import os
import re

from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis.plugmgr import RepositoryManager

import zonelist
from genesis.plugins.users.backend import *

class FirstRun(CategoryPlugin, URLHandler):
    text = 'First run wizard'
    iconfont = None
    folder = None

    def on_session_start(self):
        self._step = 1
        self._tree = TreeManager()
        self._reboot = True
        self._username = ''
        self._password = ''

    def get_ui(self):
        ui = self.app.inflate('firstrun:main')
        step = self.app.inflate('firstrun:step%i'%self._step)
        ui.append('content', step)

        if self._step == 4:
            tz_sel = [UI.SelectOption(text = x, value = x,
                        selected = False)
                        for x in zonelist.zones]
            ui.appendAll('zoneselect', *tz_sel)

        if self._step == 5:
            self._mgr = RepositoryManager(self.app.config)
            self._mgr.update_list()

            lst = self._mgr.available

            for k in sorted(lst, key=lambda x:x.name):
                row = self.app.inflate('firstrun:item')
                row.find('name').set('text', k.name)
                row.find('desc').set('text', k.description)
                row.find('icon').set('class', k.icon)
                row.find('version').set('text', k.version)
                row.find('author').set('text', k.author)
                row.find('author').set('url', k.homepage)

                req = k.str_req()

                row.find('check').set('name', 'install-'+k.id)
                if req != '':
                    row.append('reqs', UI.HelpIcon(text=req))

                ui.append('list', row)

        return ui

    def resize(self):
        shell_stdin('fdisk /dev/mmcblk0', 'd\n2\nn\np\n2\n\n\nw\n')
        f = open('/etc/cron.d/resize', 'w')
        f.write('@reboot root resize2fs /dev/mmcblk0p2\n')
        f.write('@reboot root rm /etc/cron.d/resize\n')
        f.close()
        self.app.gconfig.set('genesis', 'restartmsg', 'yes')
        self.app.gconfig.save()

    @event('form/submit')
    def on_event(self, event, params, vars=None):
        reboot = False
        if params[0] == 'splash':
            self._step = 2
        if params[0] == 'frmChangePassword':
            self._username = vars.getvalue('login', '')
            self._password = vars.getvalue('password', '')
            self._password_again = vars.getvalue('password_again', '')
            if self._username == '':
                self.put_message('err', 'The username can\'t be empty')
            elif self._password == '':
                self.put_message('err', 'The password can\'t be empty')
            elif self._password != self._password_again:
                self.put_message('err', 'The passwords don\'t match')
            elif re.search('[A-Z]|\.|:|[ ]|-$', self._username):
                self.put_message('err', 'Username must not contain capital letters, dots, colons, spaces, or end with a hyphen')
            else:
                # add Unix user
                self.backend = UsersBackend(self.app)
                users = self.backend.get_all_users()
                for u in users:
                    if u.login == self._username:
                        self.put_message('err', 'Duplicate name, please choose another')
                        self._editing = ''
                        return
                self._step = 3
        if params[0] == 'frmChangeRootPassword':
            self._root_password = vars.getvalue('root_password', '')
            self._root_password_again = vars.getvalue('root_password_again', '')
            if self._root_password == '':
                self.put_message('err', 'The password can\'t be empty')
            elif self._root_password != self._root_password_again:
                self.put_message('err', 'The passwords don\'t match')
            else:
                self._step = 4
        if params[0] == 'frmSettings':
            hostname = vars.getvalue('hostname', '')
            zone = vars.getvalue('zoneselect', 'UTC')
            resize = vars.getvalue('resize', 'False')
            gpumem = vars.getvalue('gpumem', 'False')
            ssh_as_root = vars.getvalue('ssh_as_root', 'False')
            
            if resize != '0':
                reboot = self.resize()
                self.put_message('info', 'Remember to restart your arkOS node after this wizard. To do this, click "Settings > Reboot".')
           
            if ssh_as_root != '0':
                shell('sed -i "/PermitRootLogin no/c\PermitRootLogin yes" /etc/ssh/sshd_config')
            else:
                shell('sed -i "/PermitRootLogin yes/c\PermitRootLogin no" /etc/ssh/sshd_config')
            
            if hostname != '0':
                shell('echo "' + hostname + '" > /etc/hostname')

            if gpumem != '0':
                shell('mount /dev/mmcblk0p1 /boot')
                if os.path.exists('/boot/config.txt'):
                    shell('sed -i "/gpu_mem=/c\gpu_mem=16" /boot/config.txt')
                else:
                    shell('echo "gpu_mem=16" >> /boot/config.txt')

            zone = zone.split('/')
            try:
                zonepath = os.path.join('/usr/share/zoneinfo', zone[0], zone[1])
            except IndexError:
                zonepath = os.path.join('/usr/share/zoneinfo', zone[0])
            if os.path.exists('/etc/localtime'):
                os.remove('/etc/localtime')
            os.symlink(zonepath, '/etc/localtime')
            self._step = 5
        if params[0] == 'frmPlugins':
            lst = self._mgr.available

            toinst = []

            for k in lst:
                if vars.getvalue('install-'+k.id, '0') == '1':
                    toinst.append(k.id)

            t = self._mgr.list_available()
            for y in toinst:
                for i in eval(t[y].deps):
                    for dep in i[1]:
                        if dep[0] == 'plugin' and dep[1] not in toinst:
                            self.put_message('err', ('%s can\'t be installed, as it depends on %s. Please '
                                'install that also.' % (t[y].name, t[dep[1]].name)))
                            return

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
            self.put_message('info', 'Setup complete!')

            # change root password, add Unix user, and allow sudo use
            self.backend = UsersBackend(self.app)
            self.backend.change_user_password('root', self._root_password)            
            self.backend.add_user(self._username)
            self.backend.change_user_password(self._username, self._password)
            sudofile = open('/etc/sudoers', 'r+')
            filedata = sudofile.readlines()
            filedata = ["%sudo ALL=(ALL) ALL\n" if "# %sudo" in line else line for line in filedata]
            sudofile.close()
            sudofile = open('/etc/sudoers', 'w')
            for thing in filedata:
                sudofile.write(thing)
            sudofile.close()
            shell('groupadd sudo')
            shell('usermod -a -G sudo ' + self._username)

            # add user to Genesis config
            self.app.gconfig.remove_option('users', 'admin')
            self.app.gconfig.set('users', self._username, hashpw(self._password))
            self.app.gconfig.save()
            self._step = 6
