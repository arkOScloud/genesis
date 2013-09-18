from genesis.com import *
from genesis.api import *
from genesis.plugins.security.firewall import RuleManager, FWMonitor

from servers import *


class NetworkControl(apis.API):
    # Convenience functions for routine synchronized ops
    def __init__(self, app):
        self.app = app

    def session_start(self):
        servers = ServerManager(self.app)
        servers.add('genesis', 'genesis', 'Genesis', 'gen-arkos-round',
            [('tcp', self.app.gconfig.get('genesis', 'bind_port'))])
        servers.scan_plugins()
        servers.scan_webapps()
        RuleManager(self.app).scan_servers()
        FWMonitor(self.app).regen()

    def session_stop(self):
        pass

    def port_changed(self, newport):
        pass

    def refresh(self):
        servers = ServerManager(self.app)
        servers.scan_plugins()
        RuleManager(self.app).scan_servers()
        FWMonitor(self.app).regen()

    def remove(self, id):
        servers = ServerManager(self.app)
        if servers.get_by_plugin(id) != []:
            RuleManager(self.app).remove_by_plugin(id)
            servers.remove_by_plugin(id)
            FWMonitor(self.app).regen()
