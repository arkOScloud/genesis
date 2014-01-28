from genesis.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = FMPlugin
    platform = ['any']
    
    labels = {
        'dir': 'Initial directory',
        'showhidden': 'Show hidden files?'
    }
    
    dir = '/'
    showhidden = False
   
