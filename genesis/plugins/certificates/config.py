from genesis.api import ModuleConfig
from backend import CertControl


class GeneralConfig(ModuleConfig):
    target = CertControl
    
    labels = {
        'keylength': 'Default key length',
        'keytype': 'Default key type'
    }
    
    keylength = '2048'
    keylength_opts = ['1024', '2048', '4096']
    keytype = 'RSA'
    keytype_opts = ['DSA', 'RSA']
