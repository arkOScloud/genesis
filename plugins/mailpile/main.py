import os

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager
from genesis.plugins.webapps.backend import WebappControl
from genesis.plugins.webapps.api import Webapp

import backend

class MailpilePlugin(apis.services.ServiceControlPlugin):
    text = 'Mailpile'
    iconfont = 'fa fa-envelope'
    folder = 'servers'

    def on_session_start(self):
        self._wa = apis.webapps(self.app)
        self._rc = backend.MailpileControl(self.app)

    def on_init(self):
        self.services = []
        self.site = filter(lambda x: x.name=='mailpile', self._wa.get_sites())
        self.site = self.site[0] if self.site else None

    def get_main_ui(self):
        is_installed = self._rc.is_installed()
        if is_installed == 'no' and not self._rc.setup_complete:
            ui = self.app.inflate('mailpile:setup')
            ui.find('addr').set('value', self.app.get_backend(IHostnameManager).gethostname())
            if is_installed == 'no':
                self.put_message('err', 'Your Mailpile instance does not appear to be properly configured. Please rerun this setup.')
            return ui
        ui = self.app.inflate('mailpile:main')

        url = 'http%s://%s%s'%('s' if self.site.ssl else '', self.site.addr, ':'+self.site.port if self.site.port not in ['80', '443'] else '')
        if is_installed == 'off':
            ui.find('rinfo').append(
                UI.Label(size='1', bold=True,
                    text='Your Mailpile instance is installed but not running. Please start it via the Status button.')
                )
        else:
            ui.find('rinfo').append(
                UI.Label(size='1', bold=True,
                    text='Your Mailpile site is available at '),
                )
            ui.find('rinfo').append(UI.OutLinkLabel(text=url, url=url))

        if self._editsrv:
            ui.append('main',
                UI.DialogBox(
                    UI.Formline(UI.TextInput(id='hostname', name="hostname", value=self.site.addr),
                        text="Hostname", feedback="gen-earth", iid="hostname"
                    ),
                    UI.Formline(UI.TextInput(id='hostport', name="hostport", value=self.site.port),
                        text="Port", feedback="gen-earth", iid="hostport"
                    ),
                    id='dlgEditSrv', title="Change server settings")
                )

        ui.find("launch").set("outlink", url)

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'launch':
            pass
        if params[0] == 'editsrv':
            self._editsrv = True

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmSetup':
            vaddr = True
            addr = vars.getvalue('addr', '')
            port = vars.getvalue('port', '')
            for site in apis.webapps(self.app).get_sites():
                if addr == site.addr and port == site.port:
                    vaddr = False
            if not addr or not port:
                self.put_message('err', 'Must choose an address and port!')
            elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
                self.put_message('err', 'Can\'t use the same port number as Genesis')
            elif not vaddr:
                self.put_message('err', 'This domain/subdomain and port conflicts with a website you have. '
                    'Change one of the two, or remove the site before continuing.')
            else:
                try:
                    self._rc.setup(addr, port)
                except Exception, e:
                    self.put_message('err', 'Setup failed: %s'%str(e))
        elif params[0] == 'dlgEditSrv':
            if vars.getvalue('action', '') == 'OK':
                hostname = vars.getvalue('hostname', '')
                hostport = vars.getvalue('hostport', '')
                vaddr = True
                for site in self._wa.get_sites():
                    if hostname == site.addr and hostport == site.port:
                        vaddr = False
                if hostname == '':
                    self.put_message('err', 'Must choose an address')
                elif hostport == '':
                    self.put_message('err', 'Must choose a port (default 80)')
                elif hostport == self.app.gconfig.get('genesis', 'bind_port', ''):
                    self.put_message('err', 'Can\'t use the same port number as Genesis')
                elif not vaddr:
                    self.put_message('err', 'Site must have either a different domain/subdomain or a different port')
                elif self.site.ssl and hostport == '80':
                    self.put_message('err', 'Cannot set an HTTPS site to port 80')
                elif not self.site.ssl and hostport == '443':
                    self.put_message('err', 'Cannot set an HTTP-only site to port 443')
                else:
                    w = Webapp()
                    w.name = self.site.name
                    w.stype = self.site.stype
                    w.path = self.site.path
                    w.addr = hostname
                    w.port = hostport
                    w.ssl = self.site.ssl
                    w.php = False
                    WebappControl(self.app).nginx_edit(self.site, w)
                    apis.networkcontrol(self.app).change_webapp(self.site, w)
                    self.put_message('success', 'Site edited successfully')
            self._editsrv = None
