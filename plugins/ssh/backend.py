from genesis.api import *
from genesis.utils import *
from genesis.com import *
from genesis import apis

from os import path, makedirs


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

        for s in ss:
            if s != '':
                if s[0] == '#':
                    s = s[1:]
                if s[0] == ' ':
                    s = s[1:]
                s = s.split()
                if 'PermitRootLogin' in s[0]:
                    r['root'] = True if 'yes' in s[1] else False
                if 'PubkeyAuthentication' in s[0]:
                    r['pkey'] = True if 'yes' in s[1] else False
                if 'PasswordAuthentication' in s[0]:
                    r['passwd'] = True if 'yes' in s[1] else False
                if 'PermitEmptyPasswords' in s[0]:
                    r['epasswd'] = True if 'yes' in s[1] else False

        return r

    def save(self, s):
        conf = ConfManager.get().load('ssh', '/etc/ssh/sshd_config').split('\n')
        f = ''
        for line in conf:
            if 'PermitRootLogin' in line:
                if s['root'] is True:
                    f += 'PermitRootLogin yes\n'
                else:
                    f += 'PermitRootLogin no\n'
            elif 'PubkeyAuthentication' in line:
                if s['pkey'] is True:
                    f += 'PubkeyAuthentication yes\n'
                else:
                    f += 'PubkeyAuthentication no\n'
            elif 'PasswordAuthentication' in line:
                if s['passwd'] is True:
                    f += 'PasswordAuthentication yes\n'
                else:
                    f += 'PasswordAuthentication no\n'
            elif 'PermitEmptyPasswords' in line:
                if s['epasswd'] is True:
                    f += 'PermitEmptyPasswords yes\n'
                else:
                    f += 'PermitEmptyPasswords no\n'
            else:
                f += line + '\n'
        ConfManager.get().save('ssh', '/etc/ssh/sshd_config', f)
        ConfManager.get().commit('ssh') 


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
            if not path.exists('/home/' + user + '/.ssh'):
                makedirs('/home/' + user + '/.ssh')
            if not path.exists('/home/' + user + '/.ssh/authorized_keys'):
                f = open('authorized_keys', 'w')
                f.write('')
                f.close()

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
