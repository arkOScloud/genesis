import time

from genesis.com import *
from genesis.ui import *
from genesis.utils import shell, str_fsize


class LinuxIp(Plugin):
    platform = ['Arch', 'arkos']
        
    def get_tx(self, iface):
        s = shell('ip -s link ls %s' % iface.name)
        s = s.split('\n')[5]
        s = s.split()[0] if len(s.split()) > 1 else '0'
        return int(s)
    
    def get_rx(self, iface):
        s = shell('ip -s link ls %s' % iface.name)
        s = s.split('\n')[3]
        s = s.split()[0] if len(s.split()) > 1 else '0'
        return int(s)
        
    def get_ip(self, iface):
        s = shell('ip addr list %s | grep \'inet \''%iface)
        s = s.split()[1] if len(s.split()) > 2 else '0.0.0.0'
        return s

    def detect_dev_class(self, iface):
        if iface.name[:-1] in ['ppp', 'wvdial']:
            return 'ppp'
        if iface.name[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
            return 'wireless'
        if iface.name[:-1] == 'br':
            return 'bridge'
        if iface.name[:-1] == 'tun':
            return 'tunnel'
        if iface.name == 'lo':
            return 'loopback'
        if iface.name[:-1] == 'eth':
            return 'ethernet'
        return ''

    def detect_iface_bits(self, iface):
        r = ['linux-basic']
        cls = self.detect_dev_class(iface)
        if iface.type == 'inet' and iface.addressing == 'static':
            r.append('linux-ipv4')
        if iface.type == 'inet6' and iface.addressing == 'static':
            r.append('linux-ipv6')
        if iface.addressing == 'dhcp':
            r.append('linux-dhcp')
        if cls == 'ppp':
            r.append('linux-ppp')
        if cls == 'wireless':
            r.append('linux-wlan')
        if cls == 'bridge':
            r.append('linux-bridge')
        if cls == 'tunnel':
            r.append('linux-tunnel')

        r.append('linux-ifupdown')
        return r
        
    def up(self, iface):
        shell('ip link set dev %s up' % iface.name)
        time.sleep(1)

    def down(self, iface):
        shell('ip link set dev %s down' % iface.name)
        time.sleep(1)

    def enable(self, iface):
        shell('systemctl enable netctl-auto@%s.service' % iface.name)
        time.sleep(1)

    def disable(self, iface):
        shell('systemctl disable netctl-auto@%s.service' % iface.name)
        time.sleep(1)
    
    def connup(self, conn):
        shell('netctl start %s' % conn.name)
        time.sleep(1)

    def conndown(self, conn):
        shell('netctl stop %s' % conn.name)
        time.sleep(1)

    def connenable(self, conn):
        shell('netctl enable %s' % conn.name)
        time.sleep(1)

    def conndisable(self, conn):
        shell('netctl disable %s' % conn.name)
        time.sleep(1)
