from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend

class TransmissionPlugin(apis.services.ServiceControlPlugin):
    text = 'Transmission'
    iconfont = 'gen-download'
    folder = 'apps'

    def on_session_start(self):
        self._redir = False
        self._tab = 0
        self._config = backend.TransmissionConfig(self.app)
        self._config.load()
        self.plugin_info.services[0]['ports'] = [('tcp', self._config.get('rpc-port'))]
        self.update_services()

    def get_main_ui(self):
        if self._redir:
            self._redir = False
            return self.redirapp('transmission', int(self._config.get('rpc-port')))
        else:
            ui = self.app.inflate('transmission:main')
            ui.find('tabs').set('active', self._tab)

            basic = UI.FormBox(
                UI.FormLine(
                    UI.TextInput(name='download-dir', value=self._config.get('download-dir')),
                    text='Download Directory',
                ),
                UI.Formline(
                    UI.TextInput(name='rpc-port', value=self._config.get('rpc-port')),
                    text='RPC Port',
                ),
                UI.Formline(
                    UI.Checkbox( name='rpc-whitelist-enabled', checked=self._config.get('rpc-whitelist-enabled')),
                    text='RPC Whitelist Enabled',
                ),
                id="frmBasic"
            )
            ui.append('tab0', basic)

            for k,v in sorted(self._config.items()):
                e = UI.DTR(
                    UI.IconFont(iconfont='gen-folder'),
                    UI.Label(text=k),
                    UI.Label(text=v),
                )
                ui.append('all_config', e)

            return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'launch':
            self._redir=True

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmBasic':
            if vars.getvalue('action', '') == 'OK':
                self.plugin_info.services[0]['ports'] = [('tcp', vars.getvalue('rpc-port'))]
                if int(self._config.get('rpc-port')) != int(vars.getvalue('rpc-port')):
                    self.update_services()
                self._config.set('rpc-port', int(vars.getvalue('rpc-port', '')))
                self._config.set('rpc-whitelist-enabled', vars.getvalue('rpc-whitelist-enabled', '')=='1')
                self._config.set('download-dir', vars.getvalue('download-dir', ''))
                self._config.save()
            elif vars.getvalue('action', '') == 'Cancel':
                self._config.load()
