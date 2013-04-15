from genesis.api import ModuleConfig
from logs import *


class GeneralConfig(ModuleConfig):
    target = LogsPlugin
    platform = ['any']
    
    labels = {
        'dir': 'Log directory'
    }
    
    dir = '/var/log'
   
