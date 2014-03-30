from genesis.api import ModuleConfig
from backend import MailControl


class GeneralConfig(ModuleConfig):
    target = MailControl
    
    labels = {
        'reinitialize': 'Reinitialize'
    }
    
    reinitialize = True
