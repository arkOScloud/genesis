from genesis.api import ModuleConfig
from backend import FSControl


class GeneralConfig(ModuleConfig):
    target = FSControl
    
    labels = {
        'cipher': 'Default cipher',
        'keysize': 'Default keysize',
        'dhash': 'Default hash'
    }
    
    cipher = 'aes-xts-plain64'
    cipher_opts = ['aes-xts-plain64', 'aes-cbc-essiv', 
    'aes-cbc-essiv:sha256', 'twofish-xts-plain64']
    keysize = '256'
    dhash = 'sha1'
    dhash_opts = ['sha1', 'sha256', 'sha512', 'ripemd160']
