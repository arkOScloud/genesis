from genesis.com import Plugin, implements
from genesis import apis
from genesis.utils import shell
from genesis.plugins.users.backend import UsersBackend

import hashlib
import json
import nginx
import os
import random


class Etherpad(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'Etherpad'
    icon = 'gen-pen'

    addtoblock = [
        nginx.Location('= /favicon.ico',
            nginx.Key('log_not_found', 'off'),
            nginx.Key('access_log', 'off')
        ),
    ]

    def pre_install(self, name, vars):
        eth_name = vars.getvalue('ether_admin', '')
        eth_pass = vars.getvalue('ether_pass', '')
        if not (eth_name and eth_pass):
            raise Exception('You must enter an admin name AND password!')
        #apis.databases(self.app).get_interface('MariaDB').validate(
        #    name, name, "S0me4akepa55"
        #)

    def post_install(self, name, path, vars):
        users = UsersBackend(self.app)
        users.add_user('etherpad')

        # Request a database and user to interact with it
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        dbname = name
        session_key = hashlib.sha1(str(random.random())).hexdigest()
        dbpass = session_key[0:8]
        dbase.add(dbname, conn)
        dbase.usermod(dbname, 'add', dbpass, conn)
        dbase.chperm(dbname, dbname, 'grant', conn)

        # Create/Edit the config file
        cfg = {
            "title": "Etherpad",
            "favicon": "favicon.ico",
            "ip": vars.getvalue('addr'),
            "port": vars.getvalue('port'),
            "sessionKey": session_key,
            "dbType": "mysql",
            "dbSettings": {
                "user": dbname,
                "host": "localhost",
                "password": dbpass,
                "database": dbname
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
            },
            "users": {
                vars.getvalue('ether_admin'): {
                    "password": vars.getvalue('ether_pass'),
                    "is_admin": True
                },
            },

        }
        with open(os.path.join(path, 'settings.json'), 'w') as f:
            json.dump(cfg, f, indent=4)

        # Change owner of everything in the etherpad path
        shell('chown -R etherpad ' + path)

        # node-gyp needs the HOME variable to be set
        with open(os.path.join(path, 'bin/run.sh')) as f:
            run_script = f.readlines()
        run_script.insert(1, "export HOME=%s" % path)
        with open(os.path.join(path, 'bin/run.sh'), 'w') as f:
            f.writelines(run_script)

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
        with open(os.path.join(path, 'settings.json')) as f:
            cfg = json.load(f)
            dbname = cfg["dbSettings"]["user"]
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        dbase.remove(dbname, conn)
        dbase.usermod(dbname, 'del', '', conn)

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

