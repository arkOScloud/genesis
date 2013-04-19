from genesis.ui import *
from genesis.utils import *
from genesis import apis
from genesis.com import implements, Plugin
from api import *

        
class NetworkWidget(Plugin):
    implements(apis.dashboard.IWidget)
    icon = '/dl/network-arch/down.png'
    name = 'Network monitor'
    title = None
    style = 'normal'

    def __init__(self):
        self.iface = None
        self.connection = "None"
        
    def get_ui(self, cfg, id=None):
        self.iface = cfg
        self.title = 'Network interface: %s' % cfg
        be = self.app.get_backend(INetworkConfig)
        bc = self.app.get_backend(IConnConfig)
        if not cfg in be.interfaces:
            return UI.Label(text='Interface not found')
        i = be.interfaces[cfg]
        for x in bc.connections:
            c = bc.connections[x]
            if c.interface in cfg and c.up:
                self.connection = c.name
        self.icon = '/dl/network-arch/%s.png'%('up' if i.up else 'down')
        
        ui = self.app.inflate('network-arch:widget')
        ui.find('connection').set('text', 'Connected to: ' + self.connection)
        ui.find('ip').set('text', be.get_ip(i.name))
        ui.find('in').set('text', str_fsize(be.get_rx(i)))
        ui.find('out').set('text', str_fsize(be.get_tx(i)))
        return ui
                
    def handle(self, event, params, cfg, vars=None):
        pass
    
    def get_config_dialog(self):
        be = self.app.get_backend(INetworkConfig)
        dlg = self.app.inflate('network-arch:widget-config')
        for i in be.interfaces:
            dlg.append('list', UI.Radio(
                value=i,
                text=i,
                name='iface'
            ))
        return dlg
        
    def process_config(self, vars):
        return vars.getvalue('iface', None)
