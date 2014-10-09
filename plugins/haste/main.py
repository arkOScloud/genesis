from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell
from genesis.plugins.users.backend import UsersBackend

import json
import nginx
import os


class Haste(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'Haste'
    icon = 'gen-pencil'

    addtoblock = [
        nginx.Location('/',
            nginx.Key('proxy_pass', 'http://127.0.0.1:7777'),
            nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'),
            nginx.Key('proxy_set_header', 'Host $host'),
            nginx.Key('proxy_buffering', 'off')
            )
        ]

    def pre_install(self, name, vars):
        pass

    def post_install(self, name, path, vars, dbinfo={}):
        nodectl = apis.langassist(self.app).get_interface('NodeJS')
        users = UsersBackend(self.app)

        d = json.loads(open(os.path.join(path, 'config.js'), 'r').read())
        if d["storage"]["type"] == "redis":
            d["storage"]["type"] = "file"
            d["storage"]["path"] = "./data"
            if d["storage"].has_key("host"):
                del d["storage"]["host"]
            if d["storage"].has_key("port"):
                del d["storage"]["port"]
            if d["storage"].has_key("db"):
                del d["storage"]["db"]
            if d["storage"].has_key("expire"):
                del d["storage"]["expire"]
            open(os.path.join(path, 'config.js'), 'w').write(json.dumps(d))

        nodectl.install_from_package(path)
        users.add_user('haste')

        s = self.app.get_backend(apis.services.IServiceManager)
        s.edit('haste',
            {
                'stype': 'program',
                'directory': path,
                'user': 'haste',
                'command': 'node %s'%os.path.join(path, 'server.js'),
                'autostart': 'true',
                'autorestart': 'true',
                'environment': 'NODE_ENV="production"',
                'stdout_logfile': '/var/log/haste.log',
                'stderr_logfile': '/var/log/haste.log'
            }
        )
        s.enable('haste', 'supervisor')

        # Finally, make sure that permissions are set so that Haste
        # can save its files properly.
        shell('chown -R haste ' + path)

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        users = UsersBackend(self.app)
        users.del_user('haste')
        s = self.app.get_backend(apis.services.IServiceManager)
        s.delete('haste', 'supervisor')

    def ssl_enable(self, path, cfile, kfile):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s'%name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                self.addtoblock[0].add(
                    nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
                    nginx.Key('proxy_set_header', 'X-Forwarded-Proto $scheme'),
                )
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s'%name)
        s = self.app.get_backend(apis.services.IServiceManager)

    def ssl_disable(self, path):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s'%name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s'%name)
        s = self.app.get_backend(apis.services.IServiceManager)

    def update(self, path, pkg, ver):
        # TODO: pull from Git at appropriate intervals
	pass

