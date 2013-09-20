import iptc

from genesis.com import *
from genesis.api import *
from genesis.utils import shell, cidr_to_netmask
from genesis.plugins.network.servers import ServerManager


class RuleManager(Plugin):
    abstract = True
    rules = []

    def set(self, server, allow):
        self.app.gconfig.set('security', 'fw-%s-%s'
            %(server.plugin_id, server.server_id), str(allow))
        self.app.gconfig.save()

    def get(self, server):
        for x in ServerManager(self.app).get_all():
            if x == server:
                return int(self.app.gconfig.get('security', 'fw-%s-%s'
                    %(x.plugin_id, x.server_id)))
        return False

    def get_by_id(self, id):
        for x in ServerManager(self.app).get_all():
            if x.server_id == id:
                return (x, int(self.app.gconfig.get('security', 'fw-%s-%s'
                    %(x.plugin_id, x.server_id))))
        return False

    def get_all(self):
        rules = []
        for x in ServerManager(self.app).get_all():
            rules.append((x, int(self.app.gconfig.get('security', 'fw-%s-%s'
                %(x.plugin_id, x.server_id)))))
        return rules

    def scan_servers(self):
        # Scan active servers and create entries for them when necessary
        for x in ServerManager(self.app).get_all():
            if x.plugin_id == 'arkos' and x.server_id == 'beacon' and not self.app.gconfig.has_option('security', 'fw-%s-%s'
                %(x.plugin_id, x.server_id)):
                self.set(x, 1)
            elif x.plugin_id == 'arkos' and x.server_id == 'genesis' and not self.app.gconfig.has_option('security', 'fw-%s-%s'
                %(x.plugin_id, x.server_id)):
                self.set(x, 2)
            elif not self.app.gconfig.has_option('security', 'fw-%s-%s'
                %(x.plugin_id, x.server_id)):
                self.set(x, 2)

    def clear_cache(self):
        # Compares active firewall preferences stored in config
        # to active servers, removes obsolete entries
        s = ServerManager(self.app).get_all()
        r = re.compile('fw-((?:[a-z][a-z]+))-((?:[a-z][a-z]+))',
            re.IGNORECASE)
        for o in self.app.gconfig.options('security'):
            m = r.match(o)
            if m:
                pid, sid = m.group(1), m.group(2)
                for x in s:
                    present = False
                    if x.plugin_id == pid and x.server_id == sid:
                        present = True
                    if present == False:
                        self.remove(o)

    def remove(self, server):
        # Remove an entry from firewall config
        self.app.gconfig.remove_option('security', 'fw-%s-%s'
            %(server.plugin_id, server.server_id))
        self.app.gconfig.save()

    def remove_by_plugin(self, id):
        # Remove all entries for a particular plugin
        r = re.compile('fw-((?:[a-z][a-z]+))-((?:[a-z][a-z]+))',
            re.IGNORECASE)
        for o in self.app.gconfig.options('security'):
            m = r.match(o)
            if m and m.group(1) == id:
                self.app.gconfig.remove_option('security', o)
        self.app.gconfig.save()


class FWMonitor(Plugin):
    abstract = True

    def initialize(self):
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, 'INPUT')
        c.flush()

        # Accept loopback
        r = iptc.Rule()
        r.in_interface = 'lo'
        t = iptc.Target(r, 'ACCEPT')
        r.target = t
        c.append_rule(r)

        # Accept established/related connections
        # Unfortunately this has to be done clasically
        shell('iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT')

        # Accept designated apps
        r = iptc.Rule()
        t = iptc.Target(r, 'genesis-apps')
        r.target = t
        c.append_rule(r)

        # Reject all else by default
        r = iptc.Rule()
        t = iptc.Target(r, 'DROP')
        r.target = t
        c.append_rule(r)

    def scan(self):
        # Update our local configs from what is in our iptables chain.
        # This should probably never be used, but it looks pretty.
        rm = RuleManager(self.app)
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, "genesis-apps")
        if not tb.is_chain(c):
            tb.create_chain(c)
            return
        for r in c.rules:
            m = r.matches[0]
            for s in ServerManager(self.app).get_by_port(m.dport):
                srv = rm.get(s)
                if '0.0.0.0/255.255.255.255' in r.src:
                    rm.set(s, 2)
                else:
                    rm.set(s, 1)

    def regen(self, range=[]):
        # Regenerate our chain.
        # If local ranges are not provided, get them.
        self.flush()
        if range == []:
            range = ServerManager(self.app).get_ranges()
        for x in RuleManager(self.app).get_all():
            for p in x[0].ports:
                if int(x[1]) == 2:
                    self.add(p[0], p[1], '0.0.0.0')
                elif int(x[1]) == 1:
                    for r in range:
                        self.add(p[0], p[1], r)
                else:
                    self.remove(p[0], p[1])

    def add(self, protocol, port, range=''):
        # Add rule for this port
        # If range is not provided, assume '0.0.0.0'
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, "genesis-apps")
        if not tb.is_chain(c):
            tb.create_chain(c)
        r = iptc.Rule()
        r.protocol = protocol
        if range == '' or range == '0.0.0.0':
            r.src = '0.0.0.0/255.255.255.255'
        else:
            ip, cidr = range.split('/')
            mask = cidr_to_netmask(int(cidr))
            r.src = ip + '/' + mask
        m = iptc.Match(r, protocol)
        m.dport = str(port)
        r.add_match(m)
        t = iptc.Target(r, 'ACCEPT')
        r.target = t
        c.insert_rule(r)

    def remove(self, protocol, port, range=''):
        # Remove rule(s) in our chain matching this port
        # If range is not provided, delete all rules for this port
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, "genesis-apps")
        if not tb.is_chain(c):
            return
        for r in c.rules:
            if range != '':
                if r.matches[0].dport == port and range in r.dst:
                    c.delete_rule(r)
            else:
                if r.matches[0].dport == port:
                    c.delete_rule(r)

    def find(self, protocol, port, range=''):
        # Returns true if rule is found for this port
        # If range IS provided, return true only if range is the same
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, "genesis-apps")
        if not tb.is_chain(c):
            return False
        for r in c.rules:
            if range != '':
                if r.matches[0].dport == port and range in r.dst:
                    return True
            elif range == '' and r.matches[0].dport == port:
                return True
        return False

    def flush(self):
        # Flush out our chain
        tb = iptc.Table(iptc.Table.FILTER)
        c = iptc.Chain(tb, "genesis-apps")
        if tb.is_chain(c):
            c.flush()

    def save(self):
        # Save rules to file loaded on boot
        f = open('/etc/iptables/iptables.rules', 'w')
        f.write(shell('iptables-save'))
        f.close()
