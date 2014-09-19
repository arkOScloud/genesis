import nginx
import os

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.plugins.users.backend import *
from genesis.plugins.webapps.backend import WebappControl
from genesis.utils import shell_cs, hashpw


class MailpileControl(Plugin):
    setup_complete = False

    def is_installed(self):
        # Verify the different components of the server setup
        svc = self.app.get_backend(apis.services.IServiceManager)
        if not os.path.exists('/var/lib/mailpile/.local/share/Mailpile/default') \
        or not 'mailpile' in [x.name for x in apis.webapps(self.app).get_sites()]:
            return 'no'
        elif svc.get_status('mailpile') != 'running':
            return 'off'
        else:
            return 'yes'

    def setup(self, addr, port):
        # Add the site process
        block = [
            nginx.Location('/',
                nginx.Key('proxy_pass', 'http://127.0.0.1:33411'),
                nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'),
                nginx.Key('proxy_set_header', 'Host $host'),
                nginx.Key('proxy_buffering', 'off')
            )
        ]
        WebappControl(self.app).add_reverse_proxy('mailpile', 
            '/var/lib/mailpile', addr, port, block)
        apis.networkcontrol(self.app).add_webapp(('mailpile', 'ReverseProxy', port))
        self.setup_complete = True
