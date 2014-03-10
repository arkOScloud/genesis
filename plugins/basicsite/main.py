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
        if vars.getvalue('ws-dbsel', 'None') == 'None':
            if vars.getvalue('ws-dbname', '') != '':
                raise Exception('Must choose a database type if you want to create one')
            elif vars.getvalue('ws-dbpass', '') != '':
                raise Exception('Must choose a database type if you want to create one')
        if vars.getvalue('ws-dbsel', 'None') != 'None':
            if vars.getvalue('ws-dbname', '') == '':
                raise Exception('Must choose a database name if you want to create one')
            elif vars.getvalue('ws-dbpass', '') == '':
                raise Exception('Must choose a database password if you want to create one')
            elif ' ' in vars.getvalue('ws-dbname') or '-' in vars.getvalue('ws-dbname'):
                raise Exception('Database name must not contain spaces or dashes')
            elif vars.getvalue('ws-dbname') > 16 and vars.getvalue('ws-dbsel') == 'MariaDB':
                raise Exception('Database name must be shorter than 16 characters')

    def post_install(self, name, path, vars):
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
            
        # Create a database if the user wants one
        if php:
            phpctl = apis.langassist(self.app).get_interface('PHP')
        if vars.getvalue('ws-dbsel', 'None') != 'None':
            dbtype = vars.getvalue('ws-dbsel', '')
            dbname = vars.getvalue('ws-dbname', '')
            passwd = vars.getvalue('ws-dbpass', '')
            dbase = apis.databases(self.app).get_interface(dbtype)
            if hasattr(dbase, 'connect'):
                conn = apis.databases(self.app).get_dbconn(dbtype)
                dbase.add(dbname, conn)
                dbase.usermod(dbname, 'add', passwd, conn)
                dbase.chperm(dbname, dbname, 'grant', conn)
            else:
                dbase.add(dbname)
                dbase.usermod(dbname, 'add', passwd)
                dbase.chperm(dbname, dbname, 'grant')
            if php:
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

        # Enable xcache if PHP is set
        if php:
            phpctl.enable_mod('xcache')

    def pre_remove(self, name, path):
        pass

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

    def show_opts_add(self, ui):
        type_sel = [UI.SelectOption(text='None', value='None')]
        for x in sorted(apis.databases(self.app).get_dbtypes()):
            type_sel.append(UI.SelectOption(text=x[0], value=x[0]))
        ui.appendAll('ws-dbsel', *type_sel)
