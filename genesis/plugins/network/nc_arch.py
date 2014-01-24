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
        for line in s.split('\n'):
            line = line.strip()
            if line != '':
                name = line.split(':')[1].strip()
                iface = NetworkInterface()
                iface.name = name
                self.interfaces[name] = iface
                iface.devclass = self.detect_dev_class(iface)
                iface.up = (line.find('state UP') != -1)
                iface.get_bits(self.app, self.detect_iface_bits(iface))
                if os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl-auto@' + iface.name + '.service'):
                    iface.enabled = True
                else:
                    iface.enabled = False
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
            if line != '':
                status = 0

                # Check if the connection is active
                if line.startswith('*'):
                    line = line[2:]
                    status = 1
                else:
                    line = line[2:]

                conn = NetworkConnection()
                conn.name = line
                self.connections[line] = conn
                cxnfile = open('/etc/netctl/' + line)

                # Read the options from connection configs to variable
                for thing in cxnfile.readlines():
                    if thing.startswith('#'):
                        continue
                    if not thing.strip():
                        continue
                    parse = thing.split('=')
                    parse[1] = parse[1].rstrip('\n')
                    parse[1] = parse[1].translate(None, '\"\'')
                    data[parse[0]] = parse[1]

                # Send options one-by-one to the configuration
                conn.devclass = data['Connection']
                conn.interface = data['Interface']
                if 'dhcp' in data['IP']:
                    conn.addressing = 'dhcp'
                    conn.address = ''
                    conn.gateway = ''
                else:
                    conn.addressing = 'static'
                    conn.address = data['Address']
                    try:
                        conn.gateway = data['Gateway']
                    except:
                        conn.gateway = ''
                conn.up = status
                try:
                    conn.description = data['Description']
                except:
                    conn.description = ''
                if os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl@' + conn.name + '.service'):
                    conn.enabled = True
                else:
                    conn.enabled = False
                if conn.interface[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
                    conn.essid = data['ESSID'] if data.has_key('ESSID') else 'Unknown'
                    conn.security = data['Security'] if data.has_key('Security') else 'Unknown'
                    if conn.security != 'none' and conn.security != 'wpa-configsection':
                        conn.key = data['Key']
                cxnfile.close()

    def save(self):
        return
