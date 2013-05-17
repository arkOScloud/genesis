from genesis.api import *
from main import *


class GeneralConfig(ModuleConfig):
    target = NginxBackend
    platform = ['debian', 'arch', 'arkos']
    
    labels = {
        'cfg_dir': 'Configuration directory'
    }
    
    cfg_dir = '/etc/nginx/'
