from genesis.ui import *
from genesis.api import CategoryPlugin, event
from genesis.utils import *

import backend
import re

from api import *


class NetworkPlugin(CategoryPlugin):
    text = 'Networks'
    iconfont = 'gen-network'
    folder = None

    def on_init(self):
        be = backend.Config(self.app)
        self.hosts = be.read()
        self.dns_config = self.app.get_backend(IDNSConfig)
        self.net_config = self.app.get_backend(INetworkConfig)
        self.conn_config = self.app.get_backend(IConnConfig)

    def on_session_start(self):
        self._tab = 0
        self._editing_iface = ""
        self._editing_conn = None
        self._editing = None
        self._editing_ns = None
        self._newconn = None
        
    def get_ui(self):
        self.ifacelist = []
        ui = self.app.inflate('network:main')
        ui.find('tabs').set('active', self._tab)

        """
        Network Config
        """
        cl = ui.find('connlist')
        for x in self.conn_config.connections:
            i = self.conn_config.connections[x]
            cl.append(UI.DTR(
                UI.HContainer(
                    UI.IconFont(iconfont=('gen-checkmark-circle' if i.up else ''),
                        text=('Connected' if i.up else ''),
                    ),
                    UI.Label(text=' '),
                    UI.IconFont(iconfont=('gen-link' if i.enabled else ''),
                        text=('Enabled' if i.enabled else ''),
                    ),
                ),
                UI.Label(text=i.name),
                UI.Label(text=i.devclass),
                UI.Label(text=(i.addressing+' (%s)' % self.net_config.get_ip(i.interface)) if i.up else i.addressing),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-pencil-2',
                        text='Edit', id='editconn/' + i.name),
                    UI.TipIcon(iconfont='gen-%s'%('checkmark-circle' if not i.up else 'minus-circle'), 
                        text=('Disconnect' if i.up else 'Connect'), 
                        id=('conn' + ('down' if i.up else 'up') + '/' + i.name), 
                        warning='Are you sure you wish to %s %s? This may interrupt your session.' % (('disconnect from' if i.up else 'connect to'), i.name)),
                    UI.TipIcon(iconfont='gen-%s'%('link' if not i.enabled else 'link-2'), 
                        text=('Disable' if i.enabled else 'Enable'), 
                        id=('conn' + ('disable' if i.enabled else 'enable') + '/' + i.name)),
                    UI.TipIcon(iconfont='gen-cancel-circle', 
                        text='Delete', 
                        id=('delconn/' + i.name), 
                        warning='Are you sure you wish to delete %s? This is permanent and may interrupt your session.' % (i.name))
                    ),
               ))

        nl = ui.find('devlist')
        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            ip = self.net_config.get_ip(i.name)
            tx, rx = self.net_config.get_tx(i), self.net_config.get_rx(i)
            nl.append(UI.DTR(
                UI.HContainer(
                    UI.IconFont(iconfont='gen-%s'%('checkmark-circle' if i.up else ''),
                        text=('Up' if i.up else '')
                    ),
                ),
                UI.Label(text=i.name),
                UI.Label(text=i.devclass),
                UI.Label(text=(ip if ip != '0.0.0.0' else 'none')),
                UI.Label(text=(str_fsize(tx) if tx else '-')),
                UI.Label(text=(str_fsize(rx) if rx else '-')),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-%s'%('checkmark-circle' if not i.up else 'cancel-circle'), 
                        text=('Down' if i.up else 'Up'), 
                        id=('if' + ('down' if i.up else 'up') + '/' + i.name), 
                        warning='Are you sure you wish to bring %s interface %s? This may interrupt your session.' % (('down' if i.up else 'up'), i.name)
                    ),
                    UI.TipIcon(iconfont='gen-%s'%('link' if not i.enabled else 'link-2'), 
                        text=('Disable' if i.enabled else 'Enable'), 
                        id=('if' + ('disable' if i.enabled else 'enable') + '/' + i.name))
                    ),
               ))
            self.ifacelist.extend(i.name)

        c = ui.find('conn')
        if self._newconn == True:
            c.append(
                UI.DialogBox(
                    UI.FormLine(
                        UI.SelectInput(
                            UI.SelectOption(value="ethernet", text="Wired (Ethernet)"),
                            UI.SelectOption(value="wireless", text="Wireless"),
                            id="devclass", name="devclass"
                        ),
                        text="Network type"
                    ),
                    UI.FormLine(
                        UI.SelectInput(
                            UI.SelectOption(value="dhcp", text="Automatic (DHCP)"),
                            UI.SelectOption(value="static", text="Manual (Static)"),
                            id="addressing", name="addressing"
                        ),
                        text="Addressing"
                    ), id="dlgNewConn"
                ))

        if self._editing_conn and type(self._editing_conn) == dict:
            ifaces_list = [x for x in self.net_config.interfaces]
            ui.appendAll('interface', 
                *[UI.SelectOption(id='iface-'+x, text=x, value=x) for x in ifaces_list if x != 'lo'])
            if self._editing_conn['devclass'] == 'ethernet':
                ui.find('dc-ethernet').set('selected', True)
                ui.find('devclass').set('disabled', True)
                ui.remove('fl-security')
                ui.remove('fl-essid')
                ui.remove('fl-key')
                if 'eth0' in ifaces_list:
                    ui.find('iface-eth0').set('selected', True)
            elif self._editing_conn['devclass'] == 'wireless':
                ui.find('dc-wireless').set('selected', True)
                ui.find('devclass').set('disabled', True)
                if 'wlan0' in ifaces_list:
                    ui.find('iface-wlan0').set('selected', True)
            if self._editing_conn['addressing'] == 'dhcp':
                ui.find('ad-dhcp').set('selected', True)
                ui.find('addressing').set('disabled', True)
                ui.remove('fl-address')
                ui.remove('fl-gateway')
            elif self._editing_conn['addressing'] == 'static':
                ui.find('ad-static').set('selected', True)
                ui.find('addressing').set('disabled', True)
        elif self._editing_conn and self._editing_conn != True:
            ifaces_list = [x for x in self.net_config.interfaces]
            ui.appendAll('interface', 
                *[UI.SelectOption(id='iface-'+x, text=x, value=x) for x in ifaces_list if x != 'lo'])
            ce = self._editing_conn
            ui.find('connname').set('value', ce.name)
            ui.find('connname').set('disabled', True)
            ui.find('dc-%s' % ce.devclass).set('selected', True)
            ui.find('iface-%s' % ce.interface).set('selected', True)
            ui.find('description').set('value', ce.description)
            ui.find('ad-%s' % ce.addressing).set('selected', True)
            ui.find('address').set('value', ce.address if ce.address else '')
            ui.find('gateway').set('value', ce.gateway if ce.gateway else '')
            if ce.devclass == 'wireless':
                ui.find('se-%s' % ce.security).set('selected', True)
                ui.find('essid').set('value', ce.essid if ce.essid else 'Unknown')
                if ce.security != 'none' and ce.security != 'wpa-configsection':
                    ui.find('key').set('value', ce.key if ce.key else '')
        else:
            ui.remove('dlgEditConn')


        """
        Hosts Config
        """
        ht = ui.find('hostlist')
        for h in self.hosts:
            ht.append(UI.DTR(
                UI.Label(text=h.ip),
                UI.Label(text=h.name),
                UI.Label(text=h.aliases),
                UI.HContainer(
                    UI.TipIcon(
                        iconfont='gen-pencil-2',
                        id='edit/' + str(self.hosts.index(h)),
                        text='Edit'
                    ),
                    UI.TipIcon(
                        iconfont='gen-cancel-circle',
                        id='del/' + str(self.hosts.index(h)),
                        text='Delete',
                        warning='Are you sure you wish to remove %s from the list of hosts?'%h.ip
                    )
                ),
            ))

        if self._editing != None:
            h = self.hosts[self._editing] if self._editing < len(self.hosts) else backend.Host()
            ui.find('ip').set('value', h.ip)
            ui.find('name').set('value', h.name)
            ui.find('aliases').set('value', h.aliases)
        else:
            ui.remove('dlgEdit')


        """
        DNS Config
        """
        td = ui.find('list')
        for x in range(0, len(self.dns_config.nameservers)):
            i = self.dns_config.nameservers[x]
            td.append(UI.DTR(
                UI.Label(text=i.cls),
                UI.Label(text=i.address),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-pencil-2', text='Edit', id='editns/' + str(x)),
                    UI.TipIcon(iconfont='gen-close', text='Remove', id='delns/' + str(x))
                ),
            ))

        if self._editing_ns != None:
            ns = self.dns_config.nameservers[self._editing_ns] if self._editing_ns < len(self.dns_config.nameservers) else Nameserver()
            classes = ['nameserver', 'domain', 'search', 'sortlist', 'options']
            for c in classes:
                e = ui.find('cls-' + c)
                e.set('value', c)
                e.set('selected', ns.cls==c)
            ui.find('value').set('value', ns.address)
        else:
            ui.remove('dlgEditDNS')

        return ui

    @event('button/click')
    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'ifup':
            self._tab = 0
            self.net_config.up(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifdown':
            self._tab = 0
            self.net_config.down(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifenable':
            self._tab = 0
            self.net_config.enable(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifdisable':
            self._tab = 0
            self.net_config.disable(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'connup':
            self._tab = 0
            self.conn_config.connup(self.conn_config.connections[params[1]])
        if params[0] == 'conndown':
            self._tab = 0
            self.conn_config.conndown(self.conn_config.connections[params[1]])
        if params[0] == 'connenable':
            self._tab = 0
            self.conn_config.connenable(self.conn_config.connections[params[1]])
            self.conn_config.rescan()
        if params[0] == 'conndisable':
            self._tab = 0
            self.conn_config.conndisable(self.conn_config.connections[params[1]])
            self.conn_config.rescan()
        if params[0] == 'addconn':
            self._tab = 0
            self._newconn = True
        if params[0] == 'delconn':
            self._tab = 0
            shell('rm /etc/netctl/' + params[1])
            self.conn_config.rescan()
        if params[0] == 'editconn':
            self._tab = 0
            self._editing_conn = self.conn_config.connections[params[1]]
        if params[0] == 'refresh':
            self._tab = 0
            self.net_config.rescan()
            self.conn_config.rescan()
        if params[0] == 'add':
            self._tab = 1
            self._editing = len(self.hosts)
        if params[0] == 'edit':
            self._tab = 1
            self._editing = int(params[1])
        if params[0] == 'del':
            self._tab = 1
            self.hosts.pop(int(params[1]))
            backend.Config(self.app).save(self.hosts)
        if params[0] == 'addns':
            self._tab = 2
            self._editing_ns = len(self.dns_config.nameservers) + 1
        if params[0] == 'editns':
            self._tab = 2
            self._editing_ns = int(params[1])
        if params[0] == 'delns':
            self._tab = 2
            self.dns_config.nameservers.pop(int(params[1]))
            self.dns_config.save()

    @event('dialog/submit')
    def on_dlg_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditConn':
            if vars.getvalue('action', '') == 'OK':
                ip4 = '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
                ip4regex = '^'+ip4+'$'
                ip4cidrregex = '^'+ip4+'(\/(\d|[1-2]\d|3[0-2]))$'
                if not vars.getvalue('connname', ''):
                    self.put_message('err', 'Must choose a name for the connection')
                elif re.search('\.|-|`|\\\\|\/|^test$|[ ]', vars.getvalue('connname')):
                    self.put_message('err', 'Connection name must not contain spaces, dots, dashes or special characters')
                elif vars.getvalue('addressing') == 'static' \
                and not vars.getvalue('address', ''):
                    self.put_message('err', 'Static connections must have an IP address')
                elif vars.getvalue('addressing') == 'static' \
                and not re.match(ip4cidrregex, vars.getvalue('address')):
                    self.put_message('err', 'IP address must be in the following format, with CIDR number: xxx.xxx.xxx.xxx/xx')
                elif vars.getvalue('addressing') == 'static' and vars.getvalue('gateway', '') \
                and not re.match(ip4regex, vars.getvalue('gateway')):
                    self.put_message('err', 'Gateway IP must be in the following format: xxx.xxx.xxx.xxx')
                elif vars.getvalue('devclass') == 'wireless' and not vars.getvalue('essid', ''):
                    self.put_message('err', 'Wireless connections must have an ESSID (access point name)')
                elif vars.getvalue('devclass') == 'wireless' and len(vars.getvalue('essid')) > 32:
                    self.put_message('err', 'ESSIDs cannot be longer than 32 characters')
                elif vars.getvalue('devclass') == 'wireless' \
                and re.search('^\!|^#|^;|\?|\"|\$|\[|\\\\|\]|\+', vars.getvalue('essid')):
                    self.put_message('err', 'ESSIDs cannot start with !#; or contain any the following: ?"$[]\+')
                elif vars.getvalue('devclass') == 'wireless' and vars.getvalue('security') == 'wep' \
                and len(vars.getvalue('key', '')) not in [5, 13]:
                    self.put_message('err', 'WEP keys must be either 5 or 13 characters long')
                elif vars.getvalue('devclass') == 'wireless' and vars.getvalue('security') == 'wpa' \
                and (8 > len(vars.getvalue('key', '')) or len(vars.getvalue('key', '')) > 63):
                    self.put_message('err', 'WPA keys must be between 8 and 63 characters long')
                else:
                    name = vars.getvalue('connname', '')
                    f = open('/etc/netctl/' + name, 'w')
                    f.write("# automatically generated by arkOS Genesis\n")

                    devclass = vars.getvalue('devclass', '')
                    if devclass:
                        f.write('Connection=\'' + devclass + '\'\n')

                    description = vars.getvalue('description', '')
                    if description:
                        f.write('Description=\'' + description + '\'\n')

                    interface = vars.getvalue('interface', '')
                    if interface:
                        f.write('Interface=\'' + interface + '\'\n')

                    security = vars.getvalue('security', '')
                    if security and devclass == 'wireless':
                        f.write('Security=\'' + security + '\'\n')

                    essid = vars.getvalue('essid', '')
                    if essid and devclass == 'wireless':
                        f.write('ESSID=\"' + essid + '\"\n')

                    addressing = vars.getvalue('addressing', '')
                    if addressing:
                        f.write('IP=\'' + addressing + '\'\n')

                    address = vars.getvalue('address', '')
                    if address and addressing == 'static':
                        f.write('Address=(\'' + address + '\')\n')

                    gateway = vars.getvalue('gateway', '')
                    if gateway and addressing == 'static':
                        f.write('Gateway=\'' + gateway + '\'\n')

                    key = vars.getvalue('key', '')
                    if key and devclass == 'wireless':
                        f.write('Key=\"' + key + '\"\n')

                    f.close()
                    self.conn_config.rescan()
            self._editing_conn = None
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                h = backend.Host()
                h.ip = vars.getvalue('ip', 'none')
                h.name = vars.getvalue('name', 'none')
                h.aliases = vars.getvalue('aliases', '')
                if self._editing < len(self.hosts):
                    self.hosts[self._editing] = h
                else:
                    self.hosts.append(h)
                backend.Config(self.app).save(self.hosts)
            self._editing = None
        if params[0] == 'dlgEditDNS':
            if vars.getvalue('action', '') == 'OK':
                if self._editing_ns < len(self.dns_config.nameservers):
                    i = self.dns_config.nameservers[self._editing_ns]
                else:
                    i = Nameserver()
                    self.dns_config.nameservers.append(i)
                i.cls = vars.getvalue('cls', 'nameserver')
                i.address = vars.getvalue('address', '127.0.0.1')
                self.dns_config.save()
            self._editing_ns = None
        if params[0] == 'dlgNewConn':
            if vars.getvalue('action', '') == 'OK':
                self._editing_conn = {'addressing': vars.getvalue('addressing'),
                    'devclass': vars.getvalue('devclass')}
            self._newconn = None
