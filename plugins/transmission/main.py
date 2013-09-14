from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class TransmissionPlugin(apis.services.ServiceControlPlugin):
    text = 'Transmission'
    iconfont = 'gen-download'
    folder = 'apps'
    services = [('Transmission Client', 'transmission')]

    def on_init(self):
        be = backend.TransmissionConfig(self.app)
        self.config = be.load()
        self.redir = False

    def on_session_start(self):
        pass

    def get_main_ui(self):
        if(self.redir):
            return self.redirapp(int(self.config['rpc-port']))
        else:
            ui = self.app.inflate('transmission:main')

            for k,v in sorted(self.config.items()):
                e = UI.DTR(
                    UI.IconFont(iconfont='gen-folder'),
                    UI.Label(text=k),
                    UI.Label(text=v),
                )
                ui.append('config', e)

            return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'launch':
            self.redir=True
