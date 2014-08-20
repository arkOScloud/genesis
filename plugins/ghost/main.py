from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell
from genesis.plugins.users.backend import UsersBackend

import json
import nginx
import os


class Ghost(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'Ghost'
    icon = 'gen-earth'

    addtoblock = [
        nginx.Location('/',
            nginx.Key('proxy_pass', 'http://127.0.0.1:2368'),
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

        if not os.path.exists('/usr/bin/python') and os.path.exists('/usr/bin/python'):
            os.symlink('/usr/bin/python2', '/usr/bin/python')

        d = json.loads(open(os.path.join(path, 'package.json'), 'r').read())
        del d['dependencies']['bcryptjs']
        d['dependencies']['bcrypt'] = '0.7.8'
        open(os.path.join(path, 'package.json'), 'w').write(json.dumps(d))
        d = open(os.path.join(path, 'core/server/models/user.js'), 'r').read()
        d = d.replace('bcryptjs', 'bcrypt')
        open(os.path.join(path, 'core/server/models/user.js'), 'w').write(d)

        nodectl.install_from_package(path, 'production', {'sqlite': '/usr/bin', 'python': '/usr/bin/python2'})
        users.add_user('ghost')

        s = self.app.get_backend(apis.services.IServiceManager)
        s.edit('ghost',
            {
                'stype': 'program',
                'directory': path,
                'user': 'ghost',
                'command': 'node %s'%os.path.join(path, 'index.js'),
                'autostart': 'true',
                'autorestart': 'true',
                'environment': 'NODE_ENV="production"',
                'stdout_logfile': '/var/log/ghost.log',
                'stderr_logfile': '/var/log/ghost.log'
            }
        )
        s.enable('ghost', 'supervisor')

        addr = vars.getvalue('addr', 'localhost')
        port = vars.getvalue('port', '80')

        # Get Mail settings
        mail_settings = {
            'transport' : vars.getvalue('ghost-transport', ''),
            'service' : vars.getvalue('ghost-service', ''),
            'mail_user' : vars.getvalue('ghost-mail-user', ''),
            'mail_pass' : vars.getvalue('ghost-mail-pass', ''),
            'from_address' : vars.getvalue('ghost-from-address', '')
        }

        # Create/Edit the Ghost config file
        f = open(os.path.join(path, 'config.example.js'), 'r').read()
        with open(os.path.join(path, 'config.js'), 'w') as config_file:
            f = f.replace('http://my-ghost-blog.com', 'http://'+addr+(':'+port if port != '80' else''))
            if len(set(mail_settings.values())) != 1 and\
               mail_settings['transport'] != '':
                # If the mail settings exist, add them
                f = f.replace(
                    "mail: {},",\
                    'mail: {\n'
                    "\tfromaddress: '" + mail_settings['from_address'] + "',\n"
                    "\ttransport: '" + mail_settings['transport'] + "',\n"
                    "\t\toptions: {\n"
                    "\t\t\tservice: '" + mail_settings['service'] + "',\n"
                    "\t\t\tauth: {\n"
                    "\t\t\t\tuser: '" + mail_settings['mail_user'] + "',\n"
                    "\t\t\t\tpass: '" + mail_settings['mail_pass'] + "'\n"
                    "\t\t\t}\n"
                    "\t\t}\n"
                    "},\n"
                )
            config_file.write(f)
            config_file.close()

        # Finally, make sure that permissions are set so that Ghost
        # can make adjustments and save plugins when need be.
        shell('chown -R ghost ' + path)

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        users = UsersBackend(self.app)
        users.del_user('ghost')
        s = self.app.get_backend(apis.services.IServiceManager)
        s.delete('ghost', 'supervisor')

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
        f = open(os.path.join(path, 'config.js'), 'r').read()
        with open(os.path.join(path, 'config.js'), 'w') as config_file:
            f = f.replace('production: {\n        url: \'http://', 
                'production: {\n        url: \'https://')
            config_file.write(f)
            config_file.close()
        s = self.app.get_backend(apis.services.IServiceManager)
        s.restart('ghost', 'supervisor')

    def ssl_disable(self, path):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s'%name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s'%name)
        f = open(os.path.join(path, 'config.js'), 'r').read()
        with open(os.path.join(path, 'config.js'), 'w') as config_file:
            f = f.replace('production: {\n        url: \'https://', 
                'production: {\n        url: \'http://')
            config_file.write(f)
            config_file.close()
        s = self.app.get_backend(apis.services.IServiceManager)
        s.restart('ghost', 'supervisor')

    def update(self, path, pkg, ver):
        # General update procedure
        nodectl = apis.langassist(self.app).get_interface('NodeJS')
        s = self.app.get_backend(apis.services.IServiceManager)
        out = shell('unzip -o -d %s %s' % (path, pkg), stderr=True)
        shell('chown -R ghost '+path)
        nodectl.install_from_package(path, 'production', {'sqlite': '/usr/bin', 'python': '/usr/bin/python2'})
        s.restart('ghost', 'supervisor')
