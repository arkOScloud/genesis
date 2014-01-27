from genesis.com import *
from genesis.utils import *
from genesis import apis

from api import *
from nctp_ip import *
import os

class ArchNetworkConfig(LinuxIp):
    implements(INetworkConfig)
    platform = ['Arch', 'arkos']
    
    interfaces = None
    
    def __init__(self):
        self.rescan()
    
    def rescan(self):
        self.interfaces = {}
        name = ''

        s = shell('ip -o link list')
        for x in s.split('\n'):
            if x.strip():
                name = x.split(':')[1].strip()
                iface = NetworkInterface()
                self.interfaces[name] = iface
                iface.name = name
                iface.devclass = self.detect_dev_class(iface)
                iface.up = (x.find('state UP') != -1)
                iface.get_bits(self.app, self.detect_iface_bits(iface))
                iface.enabled = True if os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl-auto@' + iface.name + '.service') \
                or os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl-ifplugd@' + iface.name + '.service') else False
                iface.editable = False

    def save(self):
        return


class ArchConnConfig(LinuxIp):
    implements(IConnConfig)
    platform = ['Arch', 'arkos']
    connections = None
    
    def __init__(self):
        self.rescan()
    
    def rescan(self):
        self.connections = {}
        name = ''

        # List connections in /etc/netctl
        netctl = shell('netctl list')
        for line in netctl.split('\n'):
            data = {}
            if line:
                # Check if the connection is active
                status = True if line.startswith('*') else False
                line = line[2:]

                c = NetworkConnection()
                self.connections[line] = c
                c.name = line

                # Read the options from connection configs to variable
                for x in open(os.path.join('/etc/netctl', line)).readlines():
                    if x.startswith('#') or not x.strip():
                        continue
                    parse = x.split('=')
                    parse[1] = parse[1].translate(None, '\"\'\n')
                    data[parse[0]] = parse[1]

                # Send options one-by-one to the configuration
                c.devclass = data['Connection']
                c.interface = data['Interface']
                if 'dhcp' in data['IP']:
                    c.addressing = 'dhcp'
                    c.address = None
                    c.gateway = None
                else:
                    c.addressing = 'static'
                    c.address = data['Address']
                    c.gateway = data['Gateway'] if data.has_key('Gateway') else None
                c.description = data['Description'] if data.has_key('Description') else None
                if c.devclass == 'wireless':
                    c.essid = data['ESSID'] if data.has_key('ESSID') else 'Unknown'
                    c.security = data['Security'] if data.has_key('Security') else 'none'
                    if c.security != 'none' and c.security != 'wpa-configsection':
                        c.key = data['Key'] if data.has_key('Key') else None
                c.enabled = True if os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl@' + c.name + '.service') else False
                c.up = status

    def save(self):
        return
