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
        self._config = backend.TransmissionConfig(self.app)
        self._config.load()

    def on_session_start(self):
        self._redir = False
        self._tab = 0

    def get_main_ui(self):
        if self._redir:
            self._redir = False
            return self.redirapp(int(self._config.get('rpc-port')))
        else:
            ui = self.app.inflate('transmission:main')
            ui.find('tabs').set('active', self._tab)

            basic = UI.Container(
                UI.Formline(
                    UI.TextInput(name='rpc-port', value=self._config.get('rpc-port')),
                    text='RPC Port',
                    ),
                UI.Formline(
                    UI.Checkbox( name='rpc-whitelist-enabled', checked=self._config.get('rpc-whitelist-enabled')=='true'),
                    text='RPC Whitelist Enabled',
                    ),
            )
            ui.append('tab0', basic)

            for k,v in sorted(self._config.items()):
                e = UI.DTR(
                    UI.IconFont(iconfont='gen-folder'),
                    UI.Label(text=k),
                    UI.TextInput(name=k, value=v),
                )
                ui.append('all_config', e)

            return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'launch':
            self._redir=True
