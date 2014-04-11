from genesis.ui import *
from genesis import apis
from genesis.com import implements, Plugin
from genesis.api import *
from genesis.utils import *
from meters import DiskUsageMeter, CpuMeter, RAMMeter, SwapMeter


class LoadWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'System load'
    iconfont = 'gen-meter'
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
    iconfont = 'gen-database'
    name = 'Memory'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        return UI.ProgressBar(value=RAMMeter(self.app).get_value(), 
            min=0, max=100)

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, vars):
        pass


class SwapWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Swap'
    iconfont = 'gen-storage'
    name = 'Swap'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        return UI.ProgressBar(value=SwapMeter(self.app).get_value(), 
            min=0, max=100)

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, vars):
        pass


class TempWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Temperature'
    iconfont = 'gen-sun'
    name = 'Temperature'
    style = 'linear'
    
    def get_ui(self, cfg, id=None):
        stat = self.app.get_backend(apis.sysstat.ISysStat)
        return UI.Label(text=stat.get_temp())
        
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        return None
        
    def process_config(self, vars):
        pass


class UptimeWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Uptime'
    iconfont = 'gen-clock'
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
    iconfont = 'gen-storage'
    name = 'Disk Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        self.title = '%s Disk Usage' % cfg
        if cfg == None:
            cfg = "total"
        m = DiskUsageMeter(self.app).prepare(cfg)
        return UI.ProgressBar(value=m.get_value(), min=0, max=m.get_max())

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
    iconfont = 'gen-busy'
    name = 'CPU Usage'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        m = CpuMeter(self.app).prepare(cfg)
        return UI.ProgressBar(value=m.get_value(), min=0, max=m.get_max())

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None
    
    def process_config(self, vars):
        pass


class ServiceWidget(Plugin):
    implements(apis.dashboard.IWidget)
    iconfont = 'gen-atom'
    name = 'Service control'
    title = None
    style = 'linear'

    def __init__(self):
        self.iface = None

    def get_ui(self, cfg, id=None):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        running = mgr.get_status(cfg) == 'running'
        self.title = cfg
        self.iconfont = 'gen-' + ('play-2' if running else 'stop')

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
