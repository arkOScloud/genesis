from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class TransmissionPlugin(apis.services.ServiceControlPlugin):
    text = 'Transmission'
    iconfont = 'gen-download'
    folder = 'applications'
    services = [('Transmission Client', 'transmission-daemon')]

    def on_init(self):
        be = backend.TransmissionConfig()
        self.config = be.load()

    def get_ui(self):
        ui = self.app.inflate('transmission:main')
        return ui