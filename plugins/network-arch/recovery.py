from genesis.api import *
from genesis.com import *


class DebianNetworkCfg(Plugin):
    implements(IConfigurable)
    name = 'Network'
    id = 'network'
    platform = ['Debian', 'Ubuntu']
    
    def list_files(self):
        dir = '/etc/network/'
        return [dir+'*', dir+'*/*', dir+'*/*/*']
    
