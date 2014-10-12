from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import hashlib
import nginx
import os
import random
import urllib


class Lychee(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = [
        nginx.Location('= /favicon.ico',
                       nginx.Key('log_not_found', 'off'),
                       nginx.Key('access_log', 'off')
                       ),
        nginx.Location('= /robots.txt',
                       nginx.Key('allow', 'all'),
                       nginx.Key('log_not_found', 'off'),
                       nginx.Key('access_log', 'off')
                       ),
        nginx.Location('/',
                       nginx.Key('try_files', '$uri $uri/ /index.php?$args')
                       ),
        nginx.Location('~ ^/(?:\.htaccess|data|config)',
                       nginx.Key('deny', 'all')
                       ),
        nginx.Location('~ \.php(?:$|/)',
                       nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
                       nginx.Key('fastcgi_read_timeout', '900s')
                       ),
        nginx.Location('~* \.(js|css|png|jpg|jpeg|gif|ico)$',
                       nginx.Key('expires', 'max'),
                       nginx.Key('log_not_found', 'off')
                       )
    ]

    def pre_install(self, name, vars):
        pass

    def post_install(self, name, path, vars, dbinfo={}):
        phpctl = apis.langassist(self.app).get_interface('PHP')

        # Create Lychee automatic configuration file
        f = open(os.path.join(path, 'data', 'config.php'), 'w')
        f.write(
            '<?php\n'
            '   if(!defined(\'LYCHEE\')) exit(\'Error: Direct access is allowed!\');\n'
            '   $dbHost = \'localhost\';\n'
            '   $dbuser = \'' + dbinfo['user'] + '\';\n'
            '   $dbPassword = \'' + dbinfo['passwd'] + '\';\n'
            '   $dbName = \'' + dbinfo['name'] + '\';\n'
            '   $dbTablePrefix = \'\';\n'
            '?>\n'
        )
        f.close()

        # Make sure that the correct PHP settings are enabled
        phpctl.enable_mod('mysql', 'mysqli', 'gd', 'zip', 'exif', 'json', 'mbstring')

        # Finally, make sure that permissions are set so that Lychee
        # can make adjustments and save plugins when need be.
        shell('chown -R http:http ' + path)

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

