from genesis.api import *
from genesis.com import *
from genesis.utils import *

import xml.etree.ElementTree as ET


class SyncthingConfig(Plugin):
    implements(IConfigurable)
    name = 'Syncthing'
    id = 'syncthing'
    iconfont = 'gen-loop-2'

    def load(self):
        self.config_tree = ET.fromstring(ConfManager.get().load('syncthing', self.configFile))
        self.config = self.config_tree.getroot()

    def save(self):
        self.config_tree.write(self.configFile)
        ConfManager.get().commit('syncthing')

    def __init__(self):
        self.configDir = '/home/syncthing/.config/syncthing'
        self.configFile = os.path.join(self.configDir, 'config.xml')
        if not os.path.exists(self.configFile):
            if not os.path.exists(self.configDir):
                os.makedirs(self.configDir)
            open(self.configFile, 'w').write()
        self.config_tree = None
        self.config = None

    def list_files(self):
        return [self.configFile]
