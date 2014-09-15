import json
import os

from genesis.api import *
from genesis.com import *
from genesis import apis

class TransmissionConfig(Plugin):
    implements(IConfigurable)
    name = 'Transmission'
    id = 'transmission'
    iconfont = 'gen-download'
    serviceName = 'transmission'

    def load(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        # The transmission package doesn't install the config file.
        # So if this is first run, start then stop the daemon to generate it.
        # TODO: Make this less awful
        if not os.path.exists(self.configFile):
            self.mgr.stop(self.serviceName)
            self.mgr.start(self.serviceName)
        s = ConfManager.get().load('transmission', self.configFile)
        self.config = json.loads(s)

    def save(self):
        wasrunning = False
        s = json.dumps(self.config)
        if self.mgr.get_status('transmission') == 'running':
            wasrunning = True
            self.mgr.stop(self.serviceName)
        ConfManager.get().save('transmission', self.configFile, s)
        ConfManager.get().commit('transmission')
        if wasrunning:
            self.mgr.start(self.serviceName)

    def get(self, key):
        return self.config[key] if self.config.has_key(key) else ""

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
