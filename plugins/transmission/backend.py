import json

from genesis.api import *
from genesis.com import *

class TransmissionConfig(Plugin):
    implements(IConfigurable)
    name = 'Transmission'
    id = 'transmission'
    iconfont = 'gen-download'

    configFile = '/var/lib/transmission/.config/transmission-daemon/settings.json'

    def load(self):
        s = ConfManager.get().load('transmission', self.configFile)
        return json.loads(s)

    def save(self, configDict):
        s = json.dumps(configDict)
        ConfManager.get().save('transmission', self.configFile, s)
        ConfManager.get().commit('transmission')

    def __init__(self):
        pass

    def list_files(self):
        return [self.configFile]
