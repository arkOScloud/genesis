from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, shell_status, download


class PHP(Plugin):
    implements(apis.langassist.ILangMgr)
    name = 'PHP'

    def install_composer(self):
        self.enable_mod('phar')
        s = shell_cs('curl -sS https://getcomposer.org/installer | php')
        if s[0] != 0:
            raise Exception('Composer download/config failed. Error: %s'%str(s[1]))
        os.rename('composer.phar', '/usr/local/bin/composer')
        os.chmod('/usr/bin/composer', 755)
        self.open_basedir('add', '/usr/local/bin')

    def verify_composer(self):
        if not shell_status('which composer') == 0:
            self.install_composer()
        if not shell_status('which composer') == 0:
            raise Exception('Composer was not installed successfully.')

    def composer_install(self, path):
        self.verify_composer()
        shell('cd %s; composer install'%path)

    def enable_mod(self, *mod):
        for x in mod:
            shell('sed -i s/\;extension=%s.so/extension=%s.so/g /etc/php/php.ini'%(x,x))

    def disable_mod(self, *mod):
        for x in mod:
            shell('sed -i s/extension=%s.so/\;extension=%s.so/g /etc/php/php.ini'%(x,x))

    def open_basedir(self, op, path):
        if op == 'add':
            ic = open('/etc/php/php.ini', 'r').readlines()
            f = open('/etc/php/php.ini', 'w')
            oc = []
            for l in ic:
                if 'open_basedir = ' in l and path not in l:
                    l = l.rstrip('\n') + ':%s\n' % path
                    oc.append(l)
                else:
                    oc.append(l)
            f.writelines(oc)
            f.close()
