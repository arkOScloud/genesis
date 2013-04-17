import time

from genesis.com import *
from genesis.ui import *
from genesis.utils import shell, str_fsize


class LinuxIp(Plugin):
    platform = ['Arch']

    def get_info(self, iface):
        ui = UI.Container( 
            UI.Formline(
                UI.HContainer(
                    UI.Image(file='/dl/network/%s.png'%('up' if iface.up else 'down')),
                    UI.Label(text=iface.name, bold=True)
                ),
                text='Interface',
            ),
            UI.Formline(
                UI.Label(text=self.get_ip(iface.name)),
                text='Address',
            ),
            UI.Formline(
                UI.Label(text='Up %s, down %s' % (
                    str_fsize(self.get_tx(iface)),
                    str_fsize(self.get_rx(iface)),
                )),
                text='Traffic',
            ),
        )
        return ui

    def get_conn_info(self, conn):
        if conn.interface[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
            ui = UI.Container( 
                UI.Formline(
                    UI.HContainer(
                        UI.Image(file='/dl/network/%s.png'%('up' if conn.up else 'down')),
                        UI.Label(text=conn.name, bold=True)
                    ),
                    text='Connection Name',
                ),
                UI.Formline(
                    UI.Label(text=conn.interface),
                    text='Interface',
                ),
                UI.Formline(
                    UI.Label(text=conn.description),
                    text='Description',
                ),
                UI.Formline(
                    UI.Label(text=(self.get_ip(conn.interface) if conn.up else '0.0.0.0')),
                    text='Address',
                ),
                UI.Formline(
                    UI.Label(text=conn.essid),
                    text='ESSID',
                ),
                UI.Formline(
                    UI.Label(text=conn.security),
                    text='Security',
                ),
            )
        else:
            ui = UI.Container( 
                UI.Formline(
                    UI.HContainer(
                        UI.Image(file='/dl/network/%s.png'%('up' if conn.up else 'down')),
                        UI.Label(text=conn.name, bold=True)
                    ),
                    text='Connection Name',
                ),
                UI.Formline(
                    UI.Label(text=conn.interface),
                    text='Description',
                ),
                UI.Formline(
                    UI.Label(text=conn.interface),
                    text='Interface',
                ),
                UI.Formline(
                    UI.Label(text=(self.get_ip(conn.interface) if conn.up else '0.0.0.0')),
                    text='Address',
                ),
            )
        return ui
        
    def get_tx(self, iface):
        s = shell('ip -s link ls %s' % iface.name)
        s = s.split('\n')[5]
        try:
            s = s.split()[0]
        except:
            s = '0'
        return int(s)
    
    def get_rx(self, iface):
        s = shell('ip -s link ls %s' % iface.name)
        s = s.split('\n')[3]
        try:
            s = s.split()[0]
        except:
            s = '0'
        return int(s)
        
    def get_ip(self, iface):
        s = shell('ip addr list %s | grep \'inet\''%iface)
        try:
            s = s.split()[1]
        except:
            s = '0.0.0.0'
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
        
