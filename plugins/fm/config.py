from genesis.api import ModuleConfig
from main import *

import os


class GeneralConfig(ModuleConfig):
    target = FMPlugin
    platform = ['any']
    
    labels = {
        'dir': 'Initial directory',
        'showhidden': 'Show hidden files?'
    }
    
    dir = '/'
    showhidden = False
   
    def __init__(self):
        self.dir = os.path.expanduser('~%s' % self.app.auth.user) \
        if hasattr(self.app, 'auth') and self.app.auth.user != 'anonymous' \
        and os.path.isdir(os.path.expanduser('~%s' % self.app.auth.user)) else '/'
