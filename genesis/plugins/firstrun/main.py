import os
import random
import re

from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis.plugmgr import RepositoryManager
from genesis.plugins.network import backend
from genesis.plugins.users.backend import *
from genesis.plugins.sysconfig import zonelist

class FirstRun(CategoryPlugin, URLHandler):
    text = 'First run wizard'
    iconfont = None
    folder = None

    def on_init(self):
        self.nb = backend.Config(self.app)
        self.ub = UsersBackend(self.app)
        self.arch = detect_architecture()

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
            if self.arch[1] != 'Raspberry Pi':
                ui.remove('rpi-ogm')
            if self.arch[1] in ['Unknown', 'General']:
                ui.remove('sdc')
            if self.arch[1] not in ['Cubieboard2', 'Cubietruck']:
                ui.remove('cbb-mac')
            else:
                mac = ':'.join(map(lambda x: "%02x" % x, 
                    [0x54, 0xb3, 0xeb, random.randint(0x00, 0x7f), 
                    random.randint(0x00, 0xff), 
                    random.randint(0x00, 0xff)]))
                ui.find('macaddr').set('value', mac)
            tz_sel = [UI.SelectOption(text = x, value = x,
                        selected = False)
                        for x in zonelist.zones]
            ui.appendAll('zoneselect', *tz_sel)

        if self._step == 5:
            self._mgr = RepositoryManager(self.app.log, self.app.config)
            try:
                self._mgr.update_list(crit=True)
            except Exception, e:
                self.put_message('err', str(e))
                self.app.log.error(str(e))

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

    def resize(self, part):
        if part == 1:
            shell_stdin('fdisk /dev/mmcblk0', 'd\nn\np\n1\n\n\nw\n')
        else:
            shell_stdin('fdisk /dev/mmcblk0', 'd\n2\nn\np\n2\n\n\nw\n')
        f = open('/etc/cron.d/resize', 'w')
        f.write('@reboot root resize2fs /dev/mmcblk0p%s\n'%part)
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
                users = self.ub.get_all_users()
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
            resize = vars.getvalue('resize', '0') if self.arch[1] in ['Cubieboard2', 'Cubietruck', 'Raspberry Pi'] else '0'
            gpumem = vars.getvalue('gpumem', '0') if self.arch[1] == 'Raspberry Pi' else '0'
            macaddr = vars.getvalue('macaddr', '') if self.arch[1] in ['Cubieboard2', 'Cubietruck'] else ''
            ssh_as_root = vars.getvalue('ssh_as_root', '0')

            if not hostname:
                self.put_message('err', 'Hostname must not be empty')
                return
            elif not re.search('^[a-zA-Z0-9.-]', hostname) or re.search('(^-.*|.*-$)', hostname):
                self.put_message('err', 'Hostname must only contain '
                    'letters, numbers, hyphens or periods, and must '
                    'not start or end with a hyphen.')
                return
            else:
                self.nb.sethostname(hostname)
            
            if resize != '0':
                reboot = self.resize(2 if self.arch[1] == 'Raspberry Pi' else 1)
                self.put_message('info', 'Remember to restart your arkOS node after this wizard. To do this, click "Settings > Reboot".')
           
            if ssh_as_root != '0':
                shell('sed -i "/PermitRootLogin no/c\PermitRootLogin yes" /etc/ssh/sshd_config')
            else:
                shell('sed -i "/PermitRootLogin yes/c\PermitRootLogin no" /etc/ssh/sshd_config')

            if gpumem != '0':
                shell('mount /dev/mmcblk0p1 /boot')
                if os.path.exists('/boot/config.txt'):
                    shell('sed -i "/gpu_mem=/c\gpu_mem=16" /boot/config.txt')
                else:
                    shell('echo "gpu_mem=16" >> /boot/config.txt')

            if macaddr != '' and self.arch[1] == 'Cubieboard2':
                open('/boot/uEnv.txt', 'w').write('extraargs=mac_addr=%s\n'%macaddr)
            elif macaddr != '' and self.arch[1] == 'Cubietruck':
                open('/etc/modprobe.d/gmac.conf', 'w').write('options sunxi_gmac mac_str="%s"\n'%macaddr)

            zone = zone.split('/')
            if len(zone) > 1:
                zonepath = os.path.join('/usr/share/zoneinfo', zone[0], zone[1])
            else:
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
                for i in t[y].deps:
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
            self.ub.change_user_password('root', self._root_password)            
            self.ub.add_user(self._username)
            self.ub.change_user_password(self._username, self._password)
            sudofile = open('/etc/sudoers', 'r+')
            filedata = sudofile.readlines()
            filedata = ["%sudo ALL=(ALL) ALL\n" if "# %sudo" in line else line for line in filedata]
            sudofile.close()
            sudofile = open('/etc/sudoers', 'w')
            for thing in filedata:
                sudofile.write(thing)
            sudofile.close()
            self.ub.add_group('sudo')
            self.ub.add_to_group(self._username, 'sudo')

            # add user to Genesis config
            self.app.gconfig.remove_option('users', 'admin')
            self.app.gconfig.set('users', self._username, hashpw(self._password))
            self.app.gconfig.save()
            self._step = 6
