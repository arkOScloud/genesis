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
        self.config = json.loads(s)

    def save(self):
        s = json.dumps(self.config)
        ConfManager.get().save('transmission', self.configFile, s)
        ConfManager.get().commit('transmission')

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value

    def items(self):
        return self.config.items()

    def __init__(self):
        self.configFile = self.app.get_config(self).cfg_file
        self.config = {}

    def list_files(self):
        return [self.configFile]

class GeneralConfig(ModuleConfig):
    target=TransmissionConfig
    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']

    labels = {
        'cfg_file': 'Configuration file'
    }

    cfg_file = '/var/lib/transmission/.config/transmission-daemon/settings.json'
