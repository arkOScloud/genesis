import os

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, shell_status, download


class Ruby(Plugin):
    implements(apis.langassist.ILangMgr)
    name = 'Ruby'

    def verify_path(self):
        profile = []
        f = open('/etc/profile', 'r')
        for l in f.readlines():
            if l.startswith('PATH="') and not '/usr/lib/ruby/gems/2.0.0/bin' in l:
                l = l.split('"\n')[0]
                l += ':/usr/lib/ruby/gems/2.0.0/bin"\n'
                profile.append(l)
                os.environ['PATH'] = os.environ['PATH'] + ':/usr/lib/ruby/gems/2.0.0/bin'
            else:
                profile.append(l)
        f.close()
        open('/etc/profile', 'w').writelines(profile)

    def install_gem(self, *gems, **kwargs):
        self.verify_path()
        gemlist = shell('gem list').split('\n')
        for x in gems:
            if not any(x==s for s in gemlist) or force:
                d = shell_cs('gem install -N --no-user-install %s' % x, stderr=True)
                if d[0] != 0:
                    self.app.log.error('Gem install \'%s\' failed: %s'%(x,str(d[1])))
                    raise Exception('Gem install \'%s\' failed. See logs for more info'%x)
