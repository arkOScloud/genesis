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

        settings_content = UI.FormBox(
            UI.FormLine(
                UI.TextInput(
                    name="welcometext",
                    value=self._config.get("welcometext", ""),
                ),
                text="Welcome Text"
            ),
            id="frmSettings"
        )
        ui.append("tab0", settings_content)

        for k, v in sorted(self._config.items()):
            if k == "serverpassword":
                continue
            e = UI.DTR(
                UI.IconFont(iconfont='gen-folder'),
                UI.Label(text=k),
                UI.Label(text=v),
            )
            ui.append('all_config', e)

        return ui

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmSettings':
            if vars.getvalue('action', '') == 'OK':
                self._config.set(
                    "welcometext",
                    vars.getvalue("welcometext", "")
                )
                self._config.save()
            elif vars.getvalue('action', '') == 'Cancel':
                self._config.load()
