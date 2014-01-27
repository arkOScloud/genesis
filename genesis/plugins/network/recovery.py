from genesis.api import *
from genesis.com import *

import os


class ArchNetworkCfg(Plugin):
    implements(IConfigurable)
    name = 'Network'
    id = 'network'
    platform = ['arch', 'arkos']
    
    def list_files(self):
        return [os.path.join('/etc/netctl', file) for file in os.listdir('/etc/netctl')
            if os.path.isfile(os.path.join('/etc/netctl', file))]

class DebianNetworkCfg(Plugin):
    implements(IConfigurable)
    name = 'Network'
    id = 'network'
    platform = ['Debian', 'Ubuntu']
    
    def list_files(self):
        dir = '/etc/network/'
        return [dir+'*', dir+'*/*', dir+'*/*/*']
    
