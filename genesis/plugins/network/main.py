from genesis.ui import *
from genesis.api import CategoryPlugin, event
from genesis.utils import *

import backend

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
        self._info = None
        self._conninfo = None
        self._editing_conn = None
        self._editing = None
        self._editing_ns = None
        
    def get_ui(self):
        self.ifacelist = []
        ui = self.app.inflate('network:main')
        ui.find('tabs').set('active', self._tab)
        cl = ui.find('connlist')

        """
        Network Config
        """

        for x in self.conn_config.connections:
            i = self.conn_config.connections[x]
            cl.append(UI.DTR(
                UI.HContainer(
                    UI.IconFont(iconfont=('gen-checkmark-circle' if i.up else ''),
                        text=('Connected' if i.up else ''),
                    ),
                ),
                UI.Label(text=i.name),
                UI.Label(text=i.devclass),
                UI.Label(text=i.addressing),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-info',
                        text='Info', id='conninfo/' + i.name),
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
            nl.append(UI.DTR(
                UI.HContainer(
                    UI.IconFont(iconfont='gen-%s'%('checkmark-circle' if i.up else ''),
                        text=('Up' if i.up else '')
                    ),
                ),
                UI.Label(text=i.name),
                UI.Label(text=i.devclass),
                UI.Label(text=self.net_config.get_ip(i.name)),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-info',
                        text='Info', id='intinfo/' + i.name),
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

        if self._info is not None:
            c.append(
                UI.DialogBox(
                    self.net_config.get_info(self.net_config.interfaces[self._info]),
                    id='dlgInfo', 
                    hidecancel=True
                ))

        if self._conninfo is not None:
            c.append(
                UI.DialogBox(
                    self.conn_config.get_conn_info(self.conn_config.connections[self._conninfo]),
                    id='dlgConnInfo', 
                    hidecancel=True
                ))

        if self._editing_conn is not None:
            if self._editing_conn is not True:
                ce = self._editing_conn
                ui.find('name').set('value', ce.name)
                ui.find('name').set('disabled', 'true')
                ui.find('devclass').set('value', ce.devclass)
                ui.find('interface').set('value', ce.interface)
                ui.find('description').set('value', ce.description)
                ui.find('addressing').set('value', ce.addressing)
                ui.find('address').set('value', ce.address)
                ui.find('gateway').set('value', ce.gateway)
                if ce.interface[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
                    ui.find('security').set('value', ce.security)
                    ui.find('essid').set('value', ce.essid)
                    if ce.security != 'none' and ce.security != 'wpa-configsection':
                        ui.find('key').set('value', ce.key)
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

        if self._editing is not None:
            try:
                h = self.hosts[self._editing]
            except:
                h = backend.Host()
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

        if self._editing_ns == None:
            ui.remove('dlgEditDNS')
        else:
            ns = self.dns_config.nameservers[self._editing_ns]
            classes = ['nameserver', 'domain', 'search', 'sortlist', 'options']
            for c in classes:
                e = ui.find('cls-' + c)
                e.set('value', c)
                e.set('selected', ns.cls==c)
            ui.find('value').set('value', ns.address)

        return ui

    @event('button/click')
    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'intinfo':
            self._tab = 0
            self._info = params[1]
        if params[0] == 'conninfo':
            self._tab = 0
            self._conninfo = params[1]
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
            self._editing_conn = True
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
        if params[0] == 'editns':
            self._tab = 2
            self._editing_ns = int(params[1])
        if params[0] == 'delns':
            self._tab = 2
            self.dns_config.nameservers.pop(int(params[1]))
            self.dns_config.save()
        if params[0] == 'addns':
            self._tab = 2
            self.dns_config.nameservers.append(Nameserver())
            self._editing_ns = len(self.dns_config.nameservers) - 1

    @event('dialog/submit')
    def on_dlg_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditConn':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('name', '')
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
                if security:
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
        if params[0] == 'dlgInfo':
            self._info = None
        if params[0] == 'dlgConnInfo':
            self._conninfo = None
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                h = backend.Host()
                h.ip = vars.getvalue('ip', 'none')
                h.name = vars.getvalue('name', 'none')
                h.aliases = vars.getvalue('aliases', '')
                try:
                    self.hosts[self._editing] = h
                except:
                    self.hosts.append(h)
                backend.Config(self.app).save(self.hosts)
            self._editing = None
        if params[0] == 'dlgEditDNS':
            if vars.getvalue('action', '') == 'OK':
                try:
                    i = self.dns_config.nameservers[self._editing_ns]
                except:
                    i = Nameserver()
                    self.dns_config.nameservers.append(i)

                i.cls = vars.getvalue('cls', 'nameserver')
                i.address = vars.getvalue('address', '127.0.0.1')
                self.dns_config.save()
            self._editing_ns = None
