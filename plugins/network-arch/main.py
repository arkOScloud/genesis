from genesis.ui import *
from genesis.api import CategoryPlugin, event
from genesis.utils import *

from api import *


class NetworkPlugin(CategoryPlugin):
    text = 'Networks'
    icon = '/dl/network-arch/icon.png'
    folder = 'system'

    def on_init(self):
        self.net_config = self.app.get_backend(INetworkConfig)
        self.conn_config = self.app.get_backend(IConnConfig)

    def on_session_start(self):
        self._editing_iface = ""
        self._info = None
        self._conninfo = None
        self._editing_conn = None
        
    def get_ui(self):
        self.ifacelist = []
        ui = self.app.inflate('network-arch:main')
        cl = ui.find('connlist')

        for x in self.conn_config.connections:
            i = self.conn_config.connections[x]
            cl.append(UI.DTR(
                            UI.HContainer(
                                UI.Icon(icon=('/dl/network-arch/up.png' if i.up else ''),
                                    text=('Connected' if i.up else ''),
                                ),
                            ),
                            UI.Label(text=i.name),
                            UI.Label(text=i.devclass),
                            UI.Label(text=i.addressing),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png',
                                    text='Info', id='conninfo/' + i.name),
                                UI.TipIcon(icon='/dl/core/ui/stock/edit.png',
                                    text='Edit', id='editconn/' + i.name),
                                UI.TipIcon(icon='/dl/core/ui/stock/service-%s.png'%('run' if not i.up else 'stop'), 
                                    text=('Disconnect' if i.up else 'Connect'), 
                                    id=('conn' + ('down' if i.up else 'up') + '/' + i.name), 
                                    warning='%s %s? This may interrupt your session.' % (('Disconnect' if i.up else 'Connect to'), i.name)),
                                UI.TipIcon(icon='/dl/core/ui/stock/status-%s.png'%('enabled' if not i.enabled else 'disabled'), 
                                    text=('Disable' if i.enabled else 'Enable'), 
                                    id=('conn' + ('disable' if i.enabled else 'enable') + '/' + i.name)),
                                UI.TipIcon(icon='/dl/core/ui/stock/delete.png', 
                                    text='Delete', 
                                    id=('delconn/' + i.name), 
                                    warning='Delete %s? This is permanent and may interrupt your session.' % (i.name))
                            ),
                           ))

        nl = ui.find('devlist')
        
        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            nl.append(UI.DTR(
                            UI.HContainer(
                                UI.Icon(icon='/dl/network-arch/%s.png'%('up' if i.up else 'down'),
                                    text=('Up' if i.up else 'Down')
                                ),
                            ),
                            UI.Label(text=i.name),
                            UI.Label(text=i.devclass),
                            UI.Label(text=self.net_config.get_ip(i.name)),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png',
                                    text='Info', id='intinfo/' + i.name),
                                UI.TipIcon(icon='/dl/core/ui/stock/service-%s.png'%('run' if not i.up else 'stop'), 
                                    text=('Down' if i.up else 'Up'), 
                                    id=('if' + ('down' if i.up else 'up') + '/' + i.name), 
                                    warning='Bring %s interface %s? This may interrupt your session.' % (('Down' if i.up else 'Up'), i.name)
                                ),
                                UI.TipIcon(icon='/dl/core/ui/stock/status-%s.png'%('enabled' if not i.enabled else 'disabled'), 
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
                if ce.devclass == 'wireless':
                    ui.find('security').set('value', ce.security)
                    ui.find('essid').set('value', ce.essid)
                    ui.find('key').set('value', ce.key)   
        else:
            ui.remove('dlgEditConn')

        return ui

    @event('button/click')
    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'intinfo':
            self._info = params[1]
        if params[0] == 'conninfo':
            self._conninfo = params[1]
        if params[0] == 'ifup':
            self.net_config.up(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifdown':
            self.net_config.down(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifenable':
            self.net_config.enable(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'ifdisable':
            self.net_config.disable(self.net_config.interfaces[params[1]])
            self.net_config.rescan()
        if params[0] == 'connup':
            self.conn_config.connup(self.conn_config.connections[params[1]])
        if params[0] == 'conndown':
            self.conn_config.conndown(self.conn_config.connections[params[1]])
        if params[0] == 'connenable':
            self.conn_config.connenable(self.conn_config.connections[params[1]])
            self.conn_config.rescan()
        if params[0] == 'conndisable':
            self.conn_config.conndisable(self.conn_config.connections[params[1]])
            self.conn_config.rescan()
        if params[0] == 'addconn':
            self._editing_conn = True
        if params[0] == 'delconn':
            shell('rm /etc/netctl/' + params[1])
            self.conn_config.rescan()
        if params[0] == 'editconn':
            self._editing_conn = self.conn_config.connections[params[1]]
        if params[0] == 'refresh':
            self.net_config.rescan()
            self.conn_config.rescan()

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

