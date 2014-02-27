from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager

import backend

class RadicalePlugin(CategoryPlugin):
    text = 'Calendar'
    iconfont = 'gen-calendar'
    folder = 'servers'

    def on_session_start(self):
        self._config = backend.RadicaleConfig(self.app)
        self._wa = apis.webapps(self.app)
        self._rc = backend.RadicaleControl(self.app)

    def on_init(self):
        self.site = filter(lambda x: x.name=='radicale', self._wa.get_sites())
        if self.site:
            self.site = self.site[0]
        else:
            self.site = None

    def get_ui(self):
        is_installed = self._rc.is_installed()
        if not self.app.get_config(self._config).first_run_complete \
        or not is_installed:
            ui = self.app.inflate('radicale:setup')
            ui.find('addr').set('value', self.app.get_backend(IHostnameManager).gethostname())
            if not is_installed:
                self.put_message('err', 'Your Calendar/Contacts server does not appear to be properly configured. Please rerun this setup.')
            return ui
        ui = self.app.inflate('radicale:main')

        ui.find('rinfo').append(
            UI.Label(size='1', bold=True,
                text='Your Calendar/Contacts server is available at http%s://%s%s'%('s' if self.site.ssl else '', self.site.addr, ':'+port if self.site.port not in ['80', '443'] else ''))
            )

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            pass

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
