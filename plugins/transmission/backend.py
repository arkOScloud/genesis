from genesis.api import *

class SambaConfig(IConfigurable):
    pass

class GeneralConfig(ModuleConfig):
    target=SambaConfig
    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']

    labels = {
        'cfg_file': 'Configuration file'
    }

    cfg_file = '/var/lib/transmission/.config/transmission-daemon/settings.json'