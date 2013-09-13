import json

from genesis.api import *
from genesis.com import *

class TransmissionConfig(Plugin):
    implements(IConfigurable)
    name = 'Transmission'
    id = 'transmission'
    iconfont = 'gen-download'

    def load(self):
        s = ConfManager.get().load('transmission', self.configFile)
        return json.loads(s)

    def save(self, configDict):
        s = json.dumps(configDict)
        ConfManager.get().save('transmission', self.configFile, s)
        ConfManager.get().commit('transmission')

    def __init__(self):
        self.configFile = self.app.get_config(self).cfg_file

    def list_files(self):
        return [self.configFile]

class GeneralConfig(ModuleConfig):
    target=TransmissionConfig
    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']

    labels = {
        'cfg_file': 'Configuration file'
    }

    cfg_file = '/var/lib/transmission/.config/transmission-daemon/settings.json'
