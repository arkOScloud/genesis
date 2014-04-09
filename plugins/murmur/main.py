from genesis.ui import *
from genesis.api import *
from genesis import apis

class MurmurPlugin(apis.services.ServiceControlPlugin):
    text = 'Mumble Server'
    iconfont = 'gen-phone'
    folder = 'servers'

    def get_main_ui(self):
        ui = self.app.inflate('transmission:main')
        return ui
