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
            d[0] + ' (' + d[1] + ')', 'gen-earth', 
            [('tcp', d[2])])
        RuleManager(self.app).set(s, 2)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def change_webapp(self, oldsite, newsite):
        servers = ServerManager(self.app)
        rm = RuleManager(self.app)
        s = servers.get(oldsite.name)[0]
        r = rm.get(s)
        rm.remove(s)
        servers.update(oldsite.name, newsite.name, 
            newsite.name + ' (' + newsite.stype + ')',
            'gen-earth', [('tcp', newsite.port)])
        rm.set(s, r)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def remove_webapp(self, sid):
        servers = ServerManager(self.app)
        s = servers.get(sid)
        if s:
            s = s[0]
        else:
            return
        RuleManager(self.app).remove(s)
        servers.remove(sid)
        FWMonitor(self.app).regen()
        FWMonitor(self.app).save()

    def port_changed(self, s):
        sm = ServerManager(self.app)
        rm = RuleManager(self.app)
        for p in s.services:
            try:
                if p['ports'] != [] and sm.get(p['binary']) != []:
                    sg = sm.get(p['binary'])[0]
                    r = rm.get(sg)
                    rm.remove(sg)
                    sm.update(p['binary'], p['binary'], p['name'], 
                        s.iconfont, p['ports'])
                    rm.set(sg, r)
                elif p['ports'] != []:
                    sg = sm.get(p['binary'])[0]
                    sm.add(s.plugin_id, p['binary'], p['name'], 
                        s.iconfont, p['ports'])
                    rm.set(sg, 2)
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
