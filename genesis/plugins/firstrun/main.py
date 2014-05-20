import os
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
        self._opts = {}
        self._veriferr = []

    def get_ui(self):
        ui = self.app.inflate('firstrun:main')
        step = self.app.inflate('firstrun:step%i'%self._step)
        ui.append('content', step)

        if detect_platform() == 'arkos':
            ui.find('welcomemsg').insertText('Welcome to arkOS')

        for x in self._veriferr:
            ui.append('veriferr', UI.SystemMessage(cls="danger", iconfont="gen-close", text=x))
        self._veriferr = []

        if self._step == 2:
            ui.find('login').set('value', self._opts['username'] if self._opts.has_key('username') else '')
            ui.find('passwd').set('value', self._opts['userpasswd'] if self._opts.has_key('userpasswd') else '')

        if self._step == 3:
            ui.find('rootpasswd').set('value', self._opts['rootpasswd'] if self._opts.has_key('rootpasswd') else '')

        if self._step == 4:
            ui.find('hostname').set('value', self._opts['hostname'] if self._opts.has_key('hostname') else 'arkos')
            ui.find('ssh_as_root').set('checked', 'True' if self._opts.has_key('ssh_as_root') and self._opts['ssh_as_root'] == '1' else 'False')

            if self.arch[1] == 'Raspberry Pi':
                ui.find('resize').set('checked', 'True' if self._opts.has_key('resize') and self._opts['resize'] == '1' else 'False')
                ui.find('gpumem').set('checked', 'True' if self._opts.has_key('gpumem') and self._opts['gpumem'] == '1' else 'False')
            else:
                ui.remove('sdc')
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
            tz = self._opts['zone'] if self._opts.has_key('zone') else 'UTC'
            tz_sel = [UI.SelectOption(text = x, value = x,
                selected=(x==tz))
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
                ui.append('ui-firstrun-appselectfield',
                    UI.AppSelect(
                        id=k.id,
                        name=k.name,
                        desc=k.description,
                        iconfont=k.icon,
                        version=k.version
                    ))

        if self._step == 6:
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Add User')), UI.DTD(UI.Label(text='Username: %s, Password: %s'%(self._opts['username'], '*'*len(self._opts['userpasswd']))))))
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Set Administrator Password')), UI.DTD(UI.Label(text='Password: %s'%('*'*len(self._opts['rootpasswd']))))))
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Set Hostname')), UI.DTD(UI.Label(text=self._opts['hostname']))))
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Set Timezone')), UI.DTD(UI.Label(text=self._opts['zone']))))
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Allow SSH as Root')), UI.DTD(UI.Label(text='Yes' if self._opts.has_key('ssh_as_root') and self._opts['ssh_as_root'] != '0' else 'No'))))
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Expand to Fit SD Card')), UI.DTD(UI.Label(text='Yes'))) if self._opts.has_key('resize') and self._opts['resize'] != '0' else None)
            ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-checkmark text-success')), UI.DTD(UI.Label(text='Adjust GPU Memory')), UI.DTD(UI.Label(text='Yes'))) if self._opts.has_key('gpumem') and self._opts['gpumem'] != '0' else None)
            for x in self._opts['toinst']+self._opts['metoo']:
                ui.append('todo', UI.DTR(UI.DTD(UI.IconFont(iconfont='gen-download text-success')), UI.DTD(UI.Label(text='Install')), UI.DTD(UI.HContainer(UI.Iconfont(iconfont=x.icon), UI.Label(text=' '+x.name)))))

        if self._opts.has_key('metoo') and self._opts['metoo']:
            ui.append('veriferr', UI.DialogBox(
                UI.Label(text=('The applications you selected require some '
                    'additional applications to be installed in order to '
                    'function properly. These will also be installed; '
                    'click OK to do this automatically or Cancel to go '
                    'back and adjust your choices.')),
                UI.ScrollContainer(
                    UI.DT(id='prereqs', width='100%', noborder='True'), 
                    width=300, height=300
                ),
                id='dlgMeToo'
            ))
            for x in self._opts['metoo']:
                ui.append('prereqs', UI.DTR(
                    UI.DTD(UI.IconFont(iconfont=x.icon), width='1'),
                    UI.DTD(UI.Label(text=x.name))
                ))

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

    def install(self, toinst):
        for k in toinst:
            try:
                self.statusmsg('Installing %s...' % k.name)
                self._mgr.install(k.id)
            except:
                pass
        ComponentManager.get().rescan()
        ConfManager.get().rescan();

    def checkdeps(self, l, a, y):
        for i in a[y.id].deps:
            for dep in a[y.id].deps[i]:
                if dep['type'] == 'plugin' and dep['package'] not in [x.id for x in self._opts['toinst']+self._opts['metoo']]:
                    for x in l:
                        if x.id == dep['package']:
                            self._opts['metoo'].append(x)
                            self.checkdeps(l, a, x)

    @event('form/submit')
    @event('dialog/submit')
    def on_event(self, event, params, vars=None):
        if params[0] == 'splash':
            self._step = 2
        if params[0] == 'frmChangePassword':
            if vars.getvalue('action', 'OK') == 'OK':
                self._opts['username'] = vars.getvalue('login', '')
                self._opts['userpasswd'] = vars.getvalue('passwd', '')
                pwdconf = vars.getvalue('passwdb', '')
                if not self._opts['username']:
                    self._veriferr.append('The username can\'t be empty. Please choose a username.')
                elif self._opts['userpasswd'] == '':
                    self._veriferr.append('The password can\'t be empty. Please choose a password.')
                elif self._opts['userpasswd'] != pwdconf:
                    self._veriferr.append('The passwords you entered don\'t match. Please try again.')
                elif re.search('[A-Z]|\.|:|[ ]|-$', self._opts['username']):
                    self._veriferr.append('The username must not contain capital letters, dots, colons, spaces, or end with a hyphen.')
                else:
                    # add Unix user
                    users = self.ub.get_all_users()
                    for x in users:
                        if x.login == self._username:
                            self._veriferr.append('A user already exists with this name. Please choose another.')
                            return
                    self._step = 3
            elif vars.getvalue('action', 'OK') == 'Back':
                self._step = 1
        if params[0] == 'frmChangeRootPassword':
            if vars.getvalue('action', 'OK') == 'OK':
                self._opts['rootpasswd'] = vars.getvalue('rootpasswd', '')
                pwdconf = vars.getvalue('rootpasswdb', '')
                if not self._opts['rootpasswd']:
                    self._veriferr.append('The password can\'t be empty')
                elif self._opts['rootpasswd'] != pwdconf:
                    self._veriferr.append('The passwords don\'t match')
                else:
                    self._step = 4
            elif vars.getvalue('action', 'OK') == 'Back':
                self._step = 2
        if params[0] == 'frmSettings':
            if vars.getvalue('action', 'OK') == 'OK':
                self._opts['hostname'] = vars.getvalue('hostname', '')
                self._opts['zone'] = vars.getvalue('zoneselect', 'UTC')
                self._opts['resize'] = vars.getvalue('resize', '0') if self.arch[1] == 'Raspberry Pi' else '0'
                self._opts['gpumem'] = vars.getvalue('gpumem', '0') if self.arch[1] == 'Raspberry Pi' else '0'
                self._opts['ssh_as_root'] = vars.getvalue('ssh_as_root', '0')

                if not self._opts['hostname']:
                    self._veriferr.append('Hostname must not be empty')
                elif not re.search('^[a-zA-Z0-9.-]', self._opts['hostname']) \
                or re.search('(^-.*|.*-$)', self._opts['hostname']):
                    self._veriferr.append('Hostname must only contain '
                        'letters, numbers, hyphens or periods, and must '
                        'not start or end with a hyphen.')
                else:
                    self._step = 5
            elif vars.getvalue('action', 'OK') == 'Back':
                self._step = 3
        if params[0] == 'frmPlugins':
            if vars.getvalue('action', 'OK') == 'OK':
                lst = self._mgr.available

                self._opts['toinst'] = []
                self._opts['metoo'] = []

                self.statusmsg('Reviewing choices...')
                for k in lst:
                    if vars.getvalue('install-'+k.id, '0') == '1':
                        self._opts['toinst'].append(k)

                self.statusmsg('Checking dependencies...')
                t = self._mgr.list_available()
                for y in self._opts['toinst']:
                    self.checkdeps(lst, t, y)

                if not self._opts['metoo']:
                    self._step = 6
            elif vars.getvalue('action', 'OK') == 'Back':
                self._step = 4
        if params[0] == 'dlgMeToo':
            if vars.getvalue('action', 'OK') == 'OK':
                self._opts['toinst'] = self._opts['toinst'] + self._opts['metoo']
                self._opts['metoo'] = []
                self._step = 6
            else:
                self._opts['metoo'] = []
                self._step = 5
        if params[0] == 'frmConfirm':
            if vars.getvalue('action', 'OK') == 'OK':
                # install apps
                self.install(self._opts['toinst'])

                # set hostname
                self.statusmsg('Setting hostname...')
                self.nb.sethostname(self._opts['hostname'])

                # set MAC address
                if macaddr != '' and self.arch[1] == 'Cubieboard2':
                    open('/boot/uEnv.txt', 'w').write('extraargs=mac_addr=%s\n'%macaddr)
                elif macaddr != '' and self.arch[1] == 'Cubietruck':
                    open('/etc/modprobe.d/gmac.conf', 'w').write('options sunxi_gmac mac_str="%s"\n'%macaddr)

                # allow SSH as root
                self.statusmsg('Setting SSH options...')
                if self._opts.has_key('ssh_as_root') and self._opts['ssh_as_root'] != '0':
                    shell('sed -i "/PermitRootLogin no/c\PermitRootLogin yes" /etc/ssh/sshd_config')
                else:
                    shell('sed -i "/PermitRootLogin yes/c\PermitRootLogin no" /etc/ssh/sshd_config')

                # set timezone
                self.statusmsg('Setting timezone...')
                zone = self._opts['zone'].split('/')
                if len(zone) > 1:
                    zonepath = os.path.join('/usr/share/zoneinfo', zone[0], zone[1])
                else:
                    zonepath = os.path.join('/usr/share/zoneinfo', zone[0])
                if os.path.exists('/etc/localtime'):
                    os.remove('/etc/localtime')
                os.symlink(zonepath, '/etc/localtime')

                # change root password, add Unix user, and allow sudo use
                self.statusmsg('Setting user preferences...')
                self.ub.change_user_password('root', self._opts['rootpasswd'])            
                self.ub.add_user(self._opts['username'])
                self.ub.change_user_password(self._opts['username'], self._opts['userpasswd'])
                sr = open('/etc/sudoers', 'r+').readlines()
                sr = ["%sudo ALL=(ALL) ALL\n" if "# %sudo" in line else line for line in sr]
                sw = open('/etc/sudoers', 'w')
                for thing in sr:
                    sw.write(thing)
                sw.close()
                self.ub.add_group('sudo')
                self.ub.add_to_group(self._opts['username'], 'sudo')

                # add user to Genesis config
                self.app.gconfig.remove_option('users', 'admin')
                self.app.gconfig.set('users', self._opts['username'], hashpw(self._opts['userpasswd']))
                self.app.gconfig.save()

                # set SD card resize (RPi only)
                if self._opts.has_key('resize') and self._opts['resize'] != '0':
                    self.statusmsg('Programming SD filesystem resize...')
                    self.resize()
                    self.put_message('info', 'Your settings have been '
                        'successfully applied. You must restart your arkOS '
                        'server for them to take effect. To do this, choose '
                        '"Restart arkOS" in the Power menu.')

                # set GPU memory (RPi only)
                if self._opts.has_key('gpumem') and self._opts['gpumem'] != '0':
                    self.statusmsg('Setting GPU memory preferences...')
                    shell('mount /dev/mmcblk0p1 /boot')
                    if os.path.exists('/boot/config.txt'):
                        shell('sed -i "/gpu_mem=/c\gpu_mem=16" /boot/config.txt')
                    else:
                        shell('echo "gpu_mem=16" >> /boot/config.txt')

                self.app.gconfig.set('genesis', 'firstrun', 'no')
                self.app.gconfig.save()
                self._opts = {}
                
                self._step = 7
            elif vars.getvalue('action', 'OK') == 'Back':
                self._step = 5
