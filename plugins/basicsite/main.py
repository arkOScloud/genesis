from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import os
import nginx


class Website(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = []

    phpblock = [
        nginx.Location('~ ^(.+?\.php)(/.*)?$',
            nginx.Key('include', 'fastcgi_params'),
            nginx.Key('fastcgi_param', 'SCRIPT_FILENAME $document_root$1'),
            nginx.Key('fastcgi_param', 'PATH_INFO $2'),
            nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
            nginx.Key('fastcgi_read_timeout', '900s'),
            )
        ]

    def pre_install(self, name, vars):
        pass

    def post_install(self, name, path, vars, dbinfo={}):
        # Write a basic index file showing that we are here
        if vars.getvalue('php', '0') == '1':
            php = True
            path = os.path.join(path, 'htdocs')
            os.mkdir(path)
            c = nginx.loadf(os.path.join('/etc/nginx/sites-available', name))
            for x in c.servers:
                if x.filter('Key', 'root'):
                    x.filter('Key', 'root')[0].value = path
            nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', name))
        else:
            php = False
            
        if php:
            phpctl = apis.langassist(self.app).get_interface('PHP')
            phpctl.enable_mod('xcache')
        if php and dbinfo and dbinfo['engine'] == 'MariaDB':
            phpctl.enable_mod('mysql')

        f = open(os.path.join(path, 'index.'+('php' if php is True else 'html')), 'w')
        f.write(
            '<html>\n'
            '<body>\n'
            '<h1>Genesis - Custom Site</h1>\n'
            '<p>Your site is online and available at '+path+'</p>\n'
            '<p>Feel free to paste your site files here</p>\n'
            '</body>\n'
            '</html>\n'
            )
        f.close()

        # Give access to httpd
        shell('chown -R http:http '+path)

    def pre_remove(self, site):
        pass

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

    def update(self, path, pkg, ver):
        pass
