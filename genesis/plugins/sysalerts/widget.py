from genesis.ui import *
from genesis import apis
from genesis.com import implements, Plugin
from genesis.api import *


class SysAlertsWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Alerts'
    iconfont = 'gen-warning'
    name = 'System alerts'
    style = 'linear'

    def get_ui(self, cfg, id=None):
        self.mon = ComponentManager.get().find('sysalerts-monitor')
        text = { 'good': 'GOOD', 'susp': 'WARNING', 'dang': 'DANGER' }
        stat = { 'good': 'info', 'susp': 'warn', 'dang': 'err' }
        ostat = 'good'
        for m in sorted(self.mon.get(), key=lambda x:x.name):
            st = self.mon.get()[m]
            if st == 'susp' and ostat == 'good':
                ostat = st
            if st == 'dang':
                ostat = st

        ui = self.app.inflate('sysalerts:widget')
        ui.find('overall').text = text[ostat]
        ui.find('overall')['class'] = 'status-cell-%s'%stat[ostat]
        return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        pass

    def process_config(self, vars):
        pass
