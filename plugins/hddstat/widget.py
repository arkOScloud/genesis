from genesis.ui import *
from genesis import apis
from genesis.com import implements, Plugin
from genesis.api import *
from genesis.utils import *
from genesis import apis
from usage import DiskUsageMeter

class DiskUsageWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Disk Usage'
    icon = '/dl/hddstat/icon.png'
    name = 'Disk Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        self.title = '%s Disk Usage' % cfg
        if cfg == None:
            cfg = "total"
        m = DiskUsageMeter(self.app).prepare(cfg)
        return UI.HContainer(
            UI.ProgressBar(value=m.get_value(), max=m.get_max(), width=220),
            UI.Label(text=str('%d%%' % m.get_value())),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        usageMeter = DiskUsageMeter(self.app)
        dialog = self.app.inflate('hddstat:widget-config')
        for option in usageMeter.get_variants():
            dialog.append('list', UI.SelectOption(
                value=option,
                text=option,
            ))
        return dialog


    def process_config(self, vars):
        return vars.getvalue('disk', None)
