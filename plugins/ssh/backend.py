from genesis.api import *
from genesis.utils import *
from genesis.com import *
from genesis import apis

import os
import pwd
import re


class SSHConfig(Plugin):
    implements(IConfigurable)
    name = 'SSH Options'
    iconfont = 'gen-console'
    id = 'ssh'

    def list_files(self):
        return ['/etc/ssh/sshd_config']

    def read(self):
        ss = ConfManager.get().load('ssh', '/etc/ssh/sshd_config').split('\n')
        r = {}
        rroot = re.compile('.*?PermitRootLogin ([^\s]+)', flags=re.IGNORECASE)
        rpkey = re.compile('.*?PubkeyAuthentication ([^\s]+)', flags=re.IGNORECASE)
        rpasswd = re.compile('.*?PasswordAuthentication ([^\s]+)', flags=re.IGNORECASE)
        repasswd = re.compile('.*?PermitEmptyPasswords ([^\s]+)', flags=re.IGNORECASE)

        for line in ss:
            if re.match(rroot, line):
                r['root'] = True if 'yes' in re.match(rroot, line).group(1) else False
            elif re.match(rpkey, line):
                r['pkey'] = True if 'yes' in re.match(rpkey, line).group(1) else False
            elif re.match(rpasswd, line):
                r['passwd'] = True if 'yes' in re.match(rpasswd, line).group(1) else False
            elif re.match(repasswd, line):
                r['epasswd'] = True if 'yes' in re.match(repasswd, line).group(1) else False

        return r

    def save(self, s):
        conf = ConfManager.get().load('ssh', '/etc/ssh/sshd_config').split('\n')
        f = ''
        rroot = re.compile('.*?PermitRootLogin ([^\s]+)', flags=re.IGNORECASE)
        rpkey = re.compile('.*?PubkeyAuthentication ([^\s]+)', flags=re.IGNORECASE)
        rpasswd = re.compile('.*?PasswordAuthentication ([^\s]+)', flags=re.IGNORECASE)
        repasswd = re.compile('.*?PermitEmptyPasswords ([^\s]+)', flags=re.IGNORECASE)
        for line in conf:
            if re.match(rroot, line):
                if s['root'] is True:
                    f += 'PermitRootLogin yes\n'
                else:
                    f += 'PermitRootLogin no\n'
            elif re.match(rpkey, line):
                if s['pkey'] is True:
                    f += 'PubkeyAuthentication yes\n'
                else:
                    f += 'PubkeyAuthentication no\n'
            elif re.match(rpasswd, line):
                if s['passwd'] is True:
                    f += 'PasswordAuthentication yes\n'
                else:
                    f += 'PasswordAuthentication no\n'
            elif re.match(repasswd, line):
                if s['epasswd'] is True:
                    f += 'PermitEmptyPasswords yes\n'
                else:
                    f += 'PermitEmptyPasswords no\n'
            else:
                f += line + '\n'
        ConfManager.get().save('ssh', '/etc/ssh/sshd_config', f)
        ConfManager.get().commit('ssh')
        mgr = self.app.get_backend(apis.services.IServiceManager)
        if mgr.get_status('sshd') == 'running':
            mgr.real_restart('sshd')


class PKey:
    def __init__(self):
        self.type = '';
        self.key = '';
        self.name = '';


class PKeysConfig(Plugin):
    implements(IConfigurable)
    name = 'SSH Public Keys'
    iconfont = 'gen-console'
    id = 'ssh_pkeys'

    def list_files(self):
        filelist = []
        for user in self.app.gconfig.options('users'):
            filelist.extend('/home/' + user + '/.ssh/authorized_keys')
        return filelist

    def read(self):
        if self.app.auth.user == 'anonymous':
            self.currentuser = 'root'
        else:
            self.currentuser = self.app.auth.user

        for user in self.app.gconfig.options('users'):
            uid = pwd.getpwnam(user).pw_uid
            user_home = ('/root' if user == 'root' else '/home/' + user)
            if not os.path.exists(user_home + '/.ssh'):
                os.makedirs(user_home + '/.ssh')
                os.chown(user_home + '/.ssh', uid, 100)
            if not os.path.exists(user_home + '/.ssh/authorized_keys'):
                f = open(user_home + '/.ssh/authorized_keys', 'w')
                f.write('')
                f.close()
                os.chown(user_home + '/.ssh/authorized_keys', uid, 100)

        ss = ConfManager.get().load('ssh_pkeys', ('/root' if self.currentuser == 'root' else '/home/' + self.currentuser) + '/.ssh/authorized_keys').split('\n')
        r = []

        for s in ss:
            if s != '' and s[0] != '#':
                k = PKey()
                s = s.split()
                try:
                    k.type = s[0]
                    k.key = s[1]
                    k.name = s[2]
                except:
                    pass
                r.append(k)

        return r

    def save(self, data):
        if self.app.auth.user == 'anonymous':
            self.currentuser = 'root'
        else:
            self.currentuser = self.app.auth.user

        d = ''
        for k in data:
            d += '%s %s %s\n' % (k.type, k.key, k.name)
        ConfManager.get().save('ssh_pkeys', ('/root' if self.currentuser == 'root' else '/home/' + self.currentuser) + '/.ssh/authorized_keys', d)
        ConfManager.get().commit('ssh_pkeys')
