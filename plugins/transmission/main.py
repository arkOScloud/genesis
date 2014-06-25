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
            ui = self.app.inflate('transmission:embed')
            ui.find('frame-frame').set('src', 'http://'+self.app.environ['HTTP_HOST'].split(':')[0]+':'+str(self._config.get('rpc-port')))
        else:
            ui = self.app.inflate('transmission:main')
            ui.find('tabs').set('active', self._tab)

            if self.app.gconfig.get('genesis', 'ssl') == '1':
                ui.find('launch').set('onclick', 'window.open("http://'+self.app.environ['HTTP_HOST'].split(':')[0]+':'+str(self._config.get('rpc-port'))+'", "_blank")')

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
                UI.Formline(
                    UI.TextInput(name='rpc-whitelist', value=self._config.get('rpc-whitelist')),
                    text='RPC IP Whitelist',
                ),
                id="frmBasic"
            )
            ui.append('tab0', basic)

            for k,v in sorted(self._config.items()):
                e = UI.Formline(
                    UI.SelectInput(UI.SelectOption(text='True', value='True', selected=v=='True'), UI.SelectOption(text='False', value='False', selected=v=='False'), name=k) \
                    if type(v) == bool else UI.TextInput(name=k, value=v),
                    text=k
                )
                ui.append('all_config', e)

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'launch':
            self._redir = True
        elif params[0] == 'goback':
            self._redir = False

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
                self._config.set('rpc-whitelist', vars.getvalue('rpc-whitelist', ''))
                self._config.save()
            elif vars.getvalue('action', '') == 'Cancel':
                self._config.load()
        elif params[0] == 'frmAdvanced':
            if vars.getvalue('action', '') == 'OK':
                for x in vars.keys():
                    if x != 'action':
                        self._config.set(x, vars.getvalue(x, self._config.get(x)))
                self._config.save()
