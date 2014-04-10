from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class MurmurPlugin(apis.services.ServiceControlPlugin):
    text = 'Mumble Server'
    iconfont = 'gen-phone'
    folder = 'servers'

    def on_session_start(self):
        self._config = backend.MurmurConfig(self.app)
        self._config.load()
        self.update_services()

    def get_main_ui(self):
        ui = self.app.inflate('murmur:main')
        return ui
