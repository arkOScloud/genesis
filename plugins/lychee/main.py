from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import nginx
import os


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
        nginx.Location('~ \.php$',
            nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
            nginx.Key('fastcgi_index', 'index.php'),
            nginx.Key('include', 'fastcgi.conf')
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
            '   $dbUser = \'' + dbinfo['user'] + '\';\n'
            '   $dbPassword = \'' + dbinfo['passwd'] + '\';\n'
            '   $dbName = \'' + dbinfo['name'] + '\';\n'
            '   $dbTablePrefix = \'\';\n'
            '?>\n'
        )
        f.close()

        # Make sure that the correct PHP settings are enabled
        phpctl.enable_mod('mysql', 'mysqli', 'gd', 'zip', 'exif', 'json', 'mbstring')

        # Rename lychee index.html to index.php to make it work with our default nginx config
        os.rename(os.path.join(path, "index.html"), os.path.join(path, "index.php"))

        # Finally, make sure that permissions are set so that Lychee
        # can make adjustments and save plugins when need be.
        shell('chown -R http:http %s' % path)

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

