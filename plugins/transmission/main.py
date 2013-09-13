from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class TransmissionPlugin(apis.services.ServiceControlPlugin):
    text = 'Transmission'
    iconfont = 'gen-download'
    folder = 'apps'
    services = [('Transmission Client', 'transmission-daemon')]

    def on_init(self):
        be = backend.TransmissionConfig(self.app)
        self.config = be.load()

    def get_ui(self):
        ui = self.app.inflate('transmission:main')

        for k,v in self.config.items():
            e = UI.DTR(
            UI.IconFont(iconfont='gen-folder'),
                    UI.Label(text=k),
                    UI.Label(text=v),
            )
            ui.append('config', e)

        return ui