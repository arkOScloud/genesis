import os

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, shell_status, download


class PHP(Plugin):
    implements(apis.langassist.ILangMgr)
    name = 'PHP'

    def install_composer(self):
        cwd = os.getcwd()
        os.environ['COMPOSER_HOME'] = '/root'
        self.enable_mod('phar')
        self.open_basedir('add', '/root')
        s = shell_cs('cd /root; curl -sS https://getcomposer.org/installer | php', stderr=True)
        if s[0] != 0:
            raise Exception('Composer download/config failed. Error: %s'%str(s[1]))
        os.rename('/root/composer.phar', '/usr/local/bin/composer')
        os.chmod('/usr/local/bin/composer', 755)
        self.open_basedir('add', '/usr/local/bin')
        shell('cd %s'%cwd)

    def verify_composer(self):
        if not shell_status('which composer') == 0:
            self.install_composer()
        if not shell_status('which composer') == 0:
            raise Exception('Composer was not installed successfully.')

    def composer_install(self, path):
        self.verify_composer()
        s = shell_cs('cd %s; composer install'%path, stderr=True)
        if s[0] != 0:
            raise Exception('Composer failed to install this app\'s bundle. Error: %s'%str(s[1]))

    def enable_mod(self, *mod):
        for x in mod:
            shell('sed -i s/\;extension=%s.so/extension=%s.so/g /etc/php/php.ini'%(x,x))

    def disable_mod(self, *mod):
        for x in mod:
            shell('sed -i s/extension=%s.so/\;extension=%s.so/g /etc/php/php.ini'%(x,x))

    def open_basedir(self, op, path):
        if op == 'add':
            with open('/etc/php/php.ini', 'r') as f:
                ic = f.readlines()
            oc = []
            for l in ic:
                if 'open_basedir = ' in l and path not in l:
                    l = l.rstrip('\n') + ':%s\n' % path
                    oc.append(l)
                else:
                    oc.append(l)
            with open('/etc/php/php.ini', 'w') as f:
                f.writelines(oc)
        elif op == 'del':
            with open('/etc/php/php.ini', 'r') as f:
                ic = f.readlines()
            oc = []
            for l in ic:
                if 'open_basedir = ' in l and path in l:
                    l = l.replace(':'+path, '')
                    l = l.replace(':'+path+'/', '')
                    oc.append(l)
                else:
                    oc.append(l)
            with open('/etc/php/php.ini', 'w') as f:
                f.writelines(oc)

    def set_large_upload_size(self):
        with open('/etc/php/php.ini', 'r') as f:
            lines = f.readlines()
        for i, l in enumerate(lines):
            if 'upload_max_filesize = ' in l:
                lines[i] = 'upload_max_filesize = 2G'
            if 'post_max_size = ' in l:
                lines[i] = 'post_max_size = 2G'
        with open('/etc/php/php.ini', 'w') as f:
            f.writelines(lines)
