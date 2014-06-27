from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis import apis

import backend


class SyncthingPlugin(apis.services.ServiceControlPlugin):
    text = 'File Shares BETA'
    iconfont = 'gen-loop-2'
    folder = 'servers'
    
    def on_session_start(self):
        self._cfg = backend.SyncthingConfig(self.app)
        self._cfg.load()

    def get_main_ui(self):
        ui = self.app.inflate('syncthing:main')
        
        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == '':
            pass

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlg':
            if vars.getvalue('action', '') == 'OK':
                pass
            self._editing = None
