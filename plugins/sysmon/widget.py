from genesis.ui import *
from genesis import apis
from genesis.com import implements, Plugin
from genesis.api import *
from genesis.utils import *
from meters import DiskUsageMeter, CpuMeter


class LoadWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'System load'
    icon = '/dl/sysmon/widget.png'
    name = 'System load'
    style = 'linear'

    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        ui = self.app.inflate('sysmon:load')
        load = stat.get_load()
        ui.find('1m').set('text', load[0])
        ui.find('5m').set('text', load[1])
        ui.find('15m').set('text', load[2])
        return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, event, params, vars):
        pass


class RamWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'RAM'
    icon = '/dl/sysmon/widget_mem.png'
    name = 'Memory'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        ru, rt = stat.get_ram()
        return UI.HContainer(
            UI.ProgressBar(value=ru, max=rt, width=220),
            UI.Label(text=str_fsize(ru)),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, vars):
        pass


class SwapWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Swap'
    icon = '/dl/sysmon/widget_swap.png'
    name = 'Swap'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        su, st = stat.get_swap()
        return UI.HContainer(
            UI.ProgressBar(value=su, max=int(st)+1, width=220),
            UI.Label(text=str_fsize(su)),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, vars):
        pass


class UptimeWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Uptime'
    icon = '/dl/core/ui/stock/server.png'
    name = 'Uptime'
    style = 'linear'
    
    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        return UI.Label(text=stat.get_uptime())
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, vars):
        pass


class DiskUsageWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Disk Usage'
    icon = '/dl/core/ui/stock/disk.png'
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
        dialog = self.app.inflate('sysmon:hddstat-config')
        for option in usageMeter.get_variants():
            dialog.append('list', UI.SelectOption(
                value=option,
                text=option,
            ))
        return dialog

    def process_config(self, vars):
        return vars.getvalue('disk', None)


class CpuWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'CPU Usage'
    icon = '/dl/core/ui/stock/cpu.png'
    name = 'CPU Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        m = CpuMeter(self.app).prepare(cfg)
        return UI.HContainer(
            UI.ProgressBar(value=m.get_value(), max=m.get_max(), width=220),
            UI.Label(text=str(m.get_value())+'%'),
        )

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None
    
    def process_config(self, vars):
        pass


class ServiceWidget(Plugin):
    implements(apis.dashboard.IWidget)
    icon = '/dl/core/ui/stock/services.png'
    name = 'Service control'
    title = None
    style = 'linear'

    def __init__(self):
        self.iface = None

    def get_ui(self, cfg, id=None):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        running = mgr.get_status(cfg) == 'running'
        self.title = cfg
        self.icon = '/dl/core/ui/stock/service-' + ('run.png' if running else 'stop.png')

        ui = self.app.inflate('sysmon:services-widget')
        if running:
            ui.remove('start')
            ui.find('stop').set('id', id+'/stop')
            ui.find('restart').set('id', id+'/restart')
        else:
            ui.remove('stop')
            ui.remove('restart')
            ui.find('start').set('id', id+'/start')
        return ui

    def handle(self, event, params, cfg, vars=None):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        if params[0] == 'start':
            mgr.start(cfg)
        if params[0] == 'stop':
            mgr.stop(cfg)
        if params[0] == 'restart':
            mgr.restart(cfg)

    def get_config_dialog(self):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        dlg = self.app.inflate('sysmon:services-config')
        for s in sorted(mgr.list_all()):
            dlg.append('list', UI.SelectOption(
                value=s.name,
                text=s.name,
            ))
        return dlg

    def process_config(self, vars):
        return vars.getvalue('svc', None)
