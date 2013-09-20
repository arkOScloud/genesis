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
        servers.add('arkos', 'genesis', 'Genesis', 'gen-arkos-round',
            [('tcp', self.app.gconfig.get('genesis', 'bind_port'))])
        servers.add('arkos', 'beacon', 'Beacon', 'gen-arkos-round',
            [('tcp', '8765')])
        servers.scan_plugins()
        servers.scan_webapps()
        RuleManager(self.app).scan_servers()
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def add_webapp(self, d):
        servers = ServerManager(self.app)
        s = servers.add('webapps', d[0], 
            d[0] + ' (' + d[1].name + ')', 'gen-earth', 
            [('tcp', d[2].getvalue('port', '80'))])
        RuleManager(self.app).set(s, 2)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def change_webapp(self, old_id, new_id, type, port):
        servers = ServerManager(self.app)
        rm = RuleManager(self.app)
        s = servers.get(old_id)[0]
        r = rm.get(s)
        rm.remove(s)
        servers.update(old_id, new_id, new_id + ' (' + type + ')',
            'gen-earth', [('tcp', port)])
        rm.set(s, r)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def remove_webapp(self, sid):
        servers = ServerManager(self.app)
        s = servers.get(sid)[0]
        RuleManager(self.app).remove(s)
        servers.remove(sid)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def port_changed(self, s):
        sm = ServerManager(self.app)
        rm = RuleManager(self.app)
        for p in s.services:
            try:
                if p[2] != [] and sm.get(p[1]) != []:
                    s = sm.get(p[1])[0]
                    r = rm.get(s)
                    rm.remove(s)
                    sm.update(p[1], p[1], p[0], 
                        c.iconfont, p[2])
                    rm.set(s, r)
                elif p[2] != []:
                    sm.add(p[1], c.plugin_id, p[0], 
                        c.iconfont, p[2])
                    rm.set(s, 2)
                FWMonitor(self.app).regen()
                FWMonitor(self.app).save()
            except IndexError:
                continue

    def refresh(self):
        servers = ServerManager(self.app)
        servers.scan_plugins()
        RuleManager(self.app).scan_servers()
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def remove(self, id):
        servers = ServerManager(self.app)
        if servers.get_by_plugin(id) != []:
            RuleManager(self.app).remove_by_plugin(id)
            servers.remove_by_plugin(id)
            FWMonitor(self.app).regen()
            FWMonitor(self.app).save()
