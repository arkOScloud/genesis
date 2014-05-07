from genesis.com import Plugin, implements
from genesis import apis
from genesis.utils import shell
from genesis.plugins.users.backend import UsersBackend

import json
import nginx
import os


class Etherpad(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'Etherpad'
    icon = 'gen-pen'

    addtoblock = []

    def pre_install(self, name, vars):
        pass

    def post_install(self, name, path, vars):
        users = UsersBackend(self.app)
        users.add_user('etherpad')

        # Create/Edit the config file
        cfg = {
            "title": "Etherpad",
            "favicon": "favicon.ico",
            "ip": vars.getvalue('addr'),
            "port": vars.getvalue('port'),
            "sessionKey": "",
            "dbType": "dirty",
            "dbSettings": {
                "filename": "var/dirty.db"
            },
            "defaultPadText": (
                "Welcome to Etherpad on arkOS!\n\nThis pad text is "
                "synchronized as you type, so that everyone viewing this page "
                "sees the same text. This allows you to collaborate seamlessly "
                "on documents!\n\nGet involved with Etherpad at "
                "http:\/\/etherpad.org, or with arkOS at http:\/\/arkos.io\n"
            ),
            "requireSession": False,
            "editOnly": False,
            "minify": True,
            "maxAge": 60 * 60 * 6,
            "abiword": None,
            "requireAuthentication": False,
            "requireAuthorization": False,
            "trustProxy": True,
            "disableIPlogging": False,
            "socketTransportProtocols": [
                "xhr-polling", "jsonp-polling", "htmlfile"
            ],
            "loglevel": "INFO",
            "logconfig": {
                "appenders": [
                    {"type": "console"}
                ]
            }
        }
        with open(os.path.join(path, 'settings.json'), 'w') as f:
            json.dump(cfg, f, indent=4)

        # Change owner of everything in the etherpad path
        shell('chown -R etherpad ' + path)

        # Make supervisor entry (and run it?)
        s = apis.orders(self.app).get_interface('supervisor')
        if s:
            s[0].order(
                'new',
                'etherpad',
                'program',
                [
                    ('directory', path),
                    ('user', 'etherpad'),
                    ('command', os.path.join(path, 'bin/run.sh')),
                    ('autostart', 'true'), ('autorestart', 'true'),
                    ('stdout_logfile', '/var/log/etherpad.log'),
                    ('stderr_logfile', '/var/log/etherpad.log')
                ]
            )

    def pre_remove(self, name, path):
        pass

    def post_remove(self, name):
        users = UsersBackend(self.app)
        users.del_user('etherpad')
        s = apis.orders(self.app).get_interface('supervisor')
        if s:
            s[0].order('del', 'etherpad')

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

