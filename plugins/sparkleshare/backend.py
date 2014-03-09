import os
import pwd
import grp
import shutil

from genesis import apis
from genesis.com import Plugin
from genesis.utils import shell, shell_cs
from genesis.plugins.users.backend import UsersBackend
from genesis.plugins.network.backend import IHostnameManager


class SSControl(Plugin):
    def setup(self):
        # Make sure Unix user/group are active
        users = UsersBackend(self.app)
        users.add_sys_with_home('sparkleshare')
        users.add_group('sparkleshare')
        users.add_to_group('sparkleshare', 'sparkleshare')
        users.change_user_param('sparkleshare', 'shell', '/usr/bin/git-shell')
        if not os.path.exists('/home/sparkleshare'):
            os.makedirs('/home/sparkleshare')

        # Configure SSH
        if not os.path.exists('/home/sparkleshare/.ssh'):
            os.makedirs('/home/sparkleshare/.ssh')
            os.chmod('/home/sparkleshare/.ssh', 700)
        if not os.path.exists('/home/sparkleshare/.ssh/authorized_keys'):
            open('/home/sparkleshare/.ssh/authorized_keys', 'w').write('')
            os.chmod('/home/sparkleshare/.ssh/authorized_keys', 600)
        f = open('/etc/ssh/sshd_config', 'r').read()
        if not '# SparkleShare' in f:
            f += '\n'
            f += '# SparkleShare\n'
            f += '# Please do not edit the above comment as it\'s used as a check by Dazzle/Genesis\n'
            f += 'Match User sparkleshare\n'
            f += '    PasswordAuthentication no\n'
            f += '    PubkeyAuthentication yes\n'
            f += '# End of SparkleShare configuration\n'
            open('/etc/ssh/sshd_config', 'w').write(f)
        self.app.get_backend(apis.services.IServiceManager).restart('sshd')

    def add_project(self, name, crypto=False):
        self.setup()
        if crypto:
            name = name + '-crypto'
        s = shell_cs('git init --quiet --bare "%s"'%os.path.join('/home/sparkleshare', name))
        if s[0] != 0:
            self.app.log.error('Creation of Git repository failed. Error:\n%s'%s[1])
            raise Exception('Creation of Git repository failed. See the logs for details')
        shell('git config --file %s receive.denyNonFastForwards true'%os.path.join('/home/sparkleshare', name, 'config'))

        # Add list of files that Git should not compress
        extensions = ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'flac', 'mp3',
            'ogg', 'oga', 'avi', 'mov', 'mpg', 'mpeg', 'mkv', 'ogv', 'ogx',
            'webm', 'zip', 'gz', 'bz', 'bz2', 'rpm', 'deb', 'tgz', 'rar',
            'ace', '7z', 'pak', 'iso', 'dmg']
        if os.path.exists(os.path.join('/home/sparkleshare', name, 'info/attributes')):
            f = open(os.path.join('/home/sparkleshare', name, 'info/attributes'), 'r').read()
        else:
            f = ''
        for x in extensions:
            f += '*.%s -delta\n' % x
            f += '*.%s -delta\n' % x.upper()
        open(os.path.join('/home/sparkleshare', name, 'info/attributes'), 'w').write(f)

        uid = pwd.getpwnam('sparkleshare').pw_uid
        gid = grp.getgrnam('sparkleshare').gr_gid
        for r, d, f in os.walk(os.path.join('/home/sparkleshare', name)):
            for x in d:
                os.chown(os.path.join(r, x), uid, gid)
                os.chmod(os.path.join(r, x), 770)
            for x in f:
                os.chown(os.path.join(r, x), uid, gid)
                os.chmod(os.path.join(r, x), 770)

        return ('ssh://sparkleshare@%s'%self.app.get_backend(IHostnameManager).gethostname().lower(),
            os.path.join('/home/sparkleshare', name))

    def get_projects(self):
        p = []
        for x in os.listdir('/home/sparkleshare'):
            if os.path.isdir(os.path.join('/home/sparkleshare', x)) and not x.startswith('.'):
                p.append(x)
        return p

    def link_client(self, cid):
        f = open('/home/sparkleshare/.ssh/authorized_keys', 'r').read()
        f += cid+'\n'
        open('/home/sparkleshare/.ssh/authorized_keys', 'w').write(f)

    def del_project(self, name):
        shutil.rmtree(os.path.join('/home/sparkleshare', name))
