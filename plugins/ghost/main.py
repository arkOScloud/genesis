from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import nginx


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

    def post_install(self, name, path, vars):
        nodectl = apis.langassist(self.app).get_interface('NodeJS')
        users = UsersBackend(self.app)

        nodectl.install_from_package(path, 'production')
        users.add_user('ghost')

        s = apis.orders(self.app).get_interface('supervisor')
        if s:
            s[0].order('new', 'ghost', 'program', 
                [('directory', path), ('user', 'ghost'), 
                ('command', 'node %s'%os.path.join(path, 'index.js')),
                ('autostart', 'true'), ('autorestart', 'true'),
                ('environment', 'NODE_ENV="production"'),
                ('stdout_logfile', '/var/log/ghost.log'),
                ('stderr_logfile', '/var/log/ghost.log')])

        """
        port = vars.getvalue('ghost-port', '2368')
        hostname = vars.getvalue('ghost-host', '127.0.0.1')
        url = vars.getvalue('ghost-url', 'my-ghost-blog.com')

        replacements = [
            ('2368', port),
            ('127.0.0.1', hostname),
            ('my-ghost-blog.com', url)
        ]

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
            for r in replacements:
                f = f.replace(r[0], r[1])
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
        """

        # Finally, make sure that permissions are set so that Ghost
        # can make adjustments and save plugins when need be.
        shell('chown -R http:http ' + path)

    def pre_remove(self, name, path):
        pass

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass
