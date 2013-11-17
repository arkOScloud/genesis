from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import hashlib
import os
import random
import urllib


class Ghost(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'Ghost'
    dpath = 'https://ghost.org/zip/ghost-0.3.3.zip'
    icon = 'gen-earth'
    php = False
    nomulti = True
    ssl = False

    addtoblock = (
        '    location / {\n'
        '        proxy_pass http://127.0.0.1:2368/;\n'
        '        proxy_set_header Host $host;\n'
        '        proxy_buffering off;\n'
        '    }\n'
        '\n'
        )

    def pre_install(self, name, vars):
        port = vars.getvalue('ghost-port', '2368')
        try:
            int(port)
        except ValueError:
            raise Exception('Invalid Port: %s' % port)

    def post_install(self, name, path, vars):
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

    def get_info(self):
        return {
            'name': 'Ghost',
            'short': 'Just a blogging platform.',
            'long': ("Ghost is a platform dedicated to one thing: Publishing."
                    "It's beautifully designed, completely customisable and"
                    "completely Open Source. Ghost allows you to write and"
                    "publish your own blog, giving you the tools to make it"
                    "easy and even fun to do. It's simple, elegant, and"
                    "designed so that you can spend less time messing with"
                    "making your blog work - and more time blogging."),
            'site': 'http://ghost.org',
            'logo': True
        }
