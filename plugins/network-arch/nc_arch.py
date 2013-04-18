from genesis.com import *
from genesis.utils import *
from genesis import apis

from api import *
from nctp_ip import *
import os

class ArchNetworkConfig(LinuxIp):
    implements(INetworkConfig)
    platform = ['Arch']
    
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
        # for iface in self.interfaces.values():
        #    for key in rc_net_keys:
        #        value = iface.params[key]
        #        if iface.addressing == 'dhcp':
        #            value = ''
        #        self.rcconf.set_param(key, value, near='interface')
        return


class ArchConnConfig(LinuxIp):
    implements(IConnConfig)
    platform = ['Arch']
    
    connections = None
    
    def __init__(self):
        self.rescan()
    
    def rescan(self):
        self.connections = {}
        name = ''

        netctl = shell('netctl list')
        for line in netctl.split('\n'):
            if line != '':
                status = 0
                if line.startswith('*'):
                    line = line[2:]
                    status = 1
                else:
                    line = line[2:]
                conn = NetworkConnection()
                conn.name = line
                self.connections[line] = conn
                data = self.read_config('/etc/netctl/' + line)
                conn.devclass = data.Connection
                conn.interface = data.Interface
                if data.IP == 'dhcp':
                    conn.addressing = 'dhcp'
                    conn.address = ''
                    conn.gateway = ''
                else:
                    conn.addressing = 'static'
                    conn.address = data.Address
                    try:
                        conn.gateway = data.Gateway
                    except NameError:
                        conn.gateway = ''
                conn.up = status
                try:
                    conn.description = data.Description
                except NameError:
                    conn.description = ''
                if os.path.exists('/etc/systemd/system/multi-user.target.wants/netctl@' + conn.name + '.service'):
                    conn.enabled = True
                else:
                    conn.enabled = False
                if conn.interface[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
                    conn.essid = data.ESSID
                    conn.security = data.Security
                    if conn.security != 'none':
                        conn.key = data.Key
                conn.editable = False

    def read_config(self, location):
        # Read a plugin's configuration file
        import imp
        f = open(location)
        data = imp.load_source('data', '', f)
        f.close()
        return data

    def save(self):
        return
