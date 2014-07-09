import os

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs


class NodeJS(Plugin):
    implements(apis.langassist.ILangMgr)
    name = 'NodeJS'

    def install(self, *mods, **kwargs):
        cd = ('cd %s;' % kwargs['install_path']) if 'install_path' in kwargs else ''
        s = shell_cs('%s npm install %s%s' % (cd, ' '.join(x for x in mods), (' --'+' --'.join(x for x in kwargs['opts']) if kwargs.has_key('opts') else '')), stderr=True)
        if s[0] != 0:
            self.app.log.error('Failed to install %s via npm; log output follows:\n%s'%(' '.join(x for x in mods),s[1]))
            raise Exception('Failed to install %s via npm, check logs for info'%' '.join(x for x in mods))

    def remove(self, *mods):
        s = shell_cs('npm uninstall %s' % ' '.join(x for x in mods), stderr=True)
        if s[0] != 0:
            self.app.log.error('Failed to remove %s via npm; log output follows:\n%s'%(' '.join(x for x in mods),s[1]))
            raise Exception('Failed to remove %s via npm, check logs for info'%' '.join(x for x in mods))

    def install_from_package(self, path, stat='production', opts={}):
        s = shell_cs('cd %s; npm install %s%s' % (path, '--'+stat if stat else '', ' --'+' --'.join(x+'='+opts[x] for x in opts) if opts else ''), stderr=True, env={'HOME': '/root'})
        if s[0] != 0:
            self.app.log.error('Failed to install %s via npm; log output follows:\n%s'%(path,s[1]))
            raise Exception('Failed to install %s via npm, check logs for info'%path)
