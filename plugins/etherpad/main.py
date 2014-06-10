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
        nginx.Location('/',
            nginx.Key('proxy_pass', 'http://127.0.0.1:2369'),
            nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'),
            nginx.Key('proxy_set_header', 'Host $host'),
            nginx.Key('proxy_buffering', 'off')
        )
    ]

    def pre_install(self, name, vars):
        eth_name = vars.getvalue('ether_admin', '')
        eth_pass = vars.getvalue('ether_pass', '')
        if not (eth_name and eth_pass):
            raise Exception('You must enter an admin name AND password'
                            'in the App Settings tab!')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        apis.databases(self.app).get_interface('MariaDB').validate(
            name, name, eth_pass, conn
        )

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
            "ip": "127.0.0.1",
            "port": "2369",
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
                "http://etherpad.org, or with arkOS at http://arkos.io\n"
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

        # node-gyp needs the HOME variable to be set
        with open(os.path.join(path, 'bin/run.sh')) as f:
            run_script = f.readlines()
        run_script.insert(1, "export HOME=%s" % path)
        with open(os.path.join(path, 'bin/run.sh'), 'w') as f:
            f.writelines(run_script)

        # Install deps right away
        if not shell(os.path.join(path, 'bin/installDeps.sh') + ' || exit 1'):
            raise RuntimeError(
                "Etherpad dependencies could not be installed.")

        # Install selected plugins
        mods = list(                            # e.g. "ep_plugin/ep_adminpads"
            str(var).split("/")[1]              #                 ^^^^^^^^^^^^
            for var in vars
            if var.startswith('ep_plugin/') and int(vars.getvalue(var))
        )
        if mods:
            mod_inst_path = os.path.join(path, "node_modules")
            if not os.path.exists(mod_inst_path):
                os.mkdir(mod_inst_path)
            nodectl = apis.langassist(self.app).get_interface('NodeJS')
            nodectl.install(*mods, install_path=mod_inst_path)

        # Make supervisor entry
        s = self.app.get_backend(apis.services.IServiceManager)
        s.edit('etherpad',
            {
                'stype': 'program',
                'directory': path,
                'user': 'etherpad',
                'command': os.path.join(path, 'bin/run.sh'),
                'autostart': 'true',
                'autorestart': 'true',
                'stdout_logfile': '/var/log/etherpad.log',
                'stderr_logfile': '/var/log/etherpad.log'
            }
        )
        s.enable('etherpad', 'supervisor')

        # Change owner of everything in the etherpad path
        shell('chown -R etherpad ' + path)
        #TODO: user auth with nginx??

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
        s = self.app.get_backend(apis.services.IServiceManager)
        s.delete('etherpad', 'supervisor')

    def ssl_enable(self, path, cfile, kfile):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s' % name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                self.addtoblock[0].add(
                    nginx.Key('proxy_set_header',
                              'X-Forwarded-For $proxy_add_x_forwarded_for'),
                    nginx.Key('proxy_set_header',
                              'X-Forwarded-Proto $scheme'),
                )
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s' % name)

    def ssl_disable(self, path):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s' % name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s' % name)

