from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs, download, detect_architecture

import hashlib
import errno
import nginx
import os
import random
import shutil


class ownCloud(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = [
        nginx.Key('error_page', '403 = /core/templates/403.php'),
        nginx.Key('error_page', '404 = /core/templates/404.php'),
        nginx.Key('client_max_body_size', '10G'),
        nginx.Key('fastcgi_buffers', '64 4K'),
        nginx.Key('rewrite', '^/caldav(.*)$ /remote.php/caldav$1 redirect'),
        nginx.Key('rewrite', '^/carddav(.*)$ /remote.php/carddav$1 redirect'),
        nginx.Key('rewrite', '^/webdav(.*)$ /remote.php/webdav$1 redirect'),
        nginx.Location('= /robots.txt',
            nginx.Key('allow', 'all'),
            nginx.Key('log_not_found', 'off'),
            nginx.Key('access_log', 'off')
            ),
        nginx.Location('~ ^/(data|config|\.ht|db_structure\.xml|README)',
            nginx.Key('deny', 'all')
            ),
        nginx.Location('/',
            nginx.Key('rewrite', '^/.well-known/host-meta /public.php?service=host-meta last'),
            nginx.Key('rewrite', '^/.well-known/host-meta.json /public.php?service=host-meta-json last'),
            nginx.Key('rewrite', '^/.well-known/carddav /remote.php/carddav/ redirect'),
            nginx.Key('rewrite', '^/.well-known/caldav /remote.php/caldav/ redirect'),
            nginx.Key('rewrite', '^(/core/doc/[^\/]+/)$ $1/index.html'),
            nginx.Key('try_files', '$uri $uri/ index.php')
            ),
        nginx.Location('~ ^(.+?\.php)(/.*)?$',
            nginx.Key('try_files', '$1 = 404'),
            nginx.Key('include', 'fastcgi_params'),
            nginx.Key('fastcgi_param', 'SCRIPT_FILENAME $document_root$1'),
            nginx.Key('fastcgi_param', 'PATH_INFO $2'),
            nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
            nginx.Key('fastcgi_read_timeout', '900s')
            ),
        nginx.Location('~* ^.+\.(jpg|jpeg|gif|bmp|ico|png|css|js|swf)$',
            nginx.Key('expires', '30d'),
            nginx.Key('access_log', 'off')
            )
        ]

    def pre_install(self, name, vars):
        dbname = vars.getvalue('oc-dbname', '')
        dbpasswd = vars.getvalue('oc-dbpasswd', '')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        if dbname and dbpasswd:
            apis.databases(self.app).get_interface('MariaDB').validate(
                dbname, dbname, dbpasswd, conn)
        elif dbname:
            raise Exception('You must enter a database password if you specify a database name!')
        elif dbpasswd:
            raise Exception('You must enter a database name if you specify a database password!')
        if vars.getvalue('oc-username', '') == '':
            raise Exception('Must choose an ownCloud username')
        elif vars.getvalue('oc-logpasswd', '') == '':
            raise Exception('Must choose an ownCloud password')

    def post_install(self, name, path, vars):
        phpctl = apis.langassist(self.app).get_interface('PHP')
        datadir = ''
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        if vars.getvalue('oc-dbname', '') == '':
            dbname = name
        else:
            dbname = vars.getvalue('oc-dbname')
        secret_key = hashlib.sha1(str(random.random())).hexdigest()
        if vars.getvalue('oc-dbpasswd', '') == '':
            passwd = secret_key[0:8]
        else:
            passwd = vars.getvalue('oc-dbpasswd')
        username = vars.getvalue('oc-username')
        logpasswd = vars.getvalue('oc-logpasswd')

        # Request a database and user to interact with it
        dbase.add(dbname, conn)
        dbase.usermod(dbname, 'add', passwd, conn)
        dbase.chperm(dbname, dbname, 'grant', conn)

        # Set ownership as necessary
        if not os.path.exists(os.path.join(path, 'data')):
            os.makedirs(os.path.join(path, 'data'))
        shell('chown -R http:http '+os.path.join(path, 'apps'))
        shell('chown -R http:http '+os.path.join(path, 'data'))
        shell('chown -R http:http '+os.path.join(path, 'config'))

        # If there is a custom path for the data directory, do the magic
        if vars.getvalue('oc-ddir', '') != '':
            datadir = vars.getvalue('oc-ddir')
            if not os.path.exists(os.path.join(datadir if datadir else path, 'data')):
                os.makedirs(os.path.join(datadir if datadir else path, 'data'))
            shell('chown -R http:http '+os.path.join(datadir if datadir else path, 'data'))
            phpctl.open_basedir('add', datadir)

        # Create ownCloud automatic configuration file
        f = open(os.path.join(path, 'config', 'autoconfig.php'), 'w')
        f.write(
            '<?php\n'
            '   $AUTOCONFIG = array(\n'
            '   "adminlogin" => "'+username+'",\n'
            '   "adminpass" => "'+logpasswd+'",\n'
            '   "dbtype" => "mysql",\n'
            '   "dbname" => "'+dbname+'",\n'
            '   "dbuser" => "'+dbname+'",\n'
            '   "dbpass" => "'+passwd+'",\n'
            '   "dbhost" => "localhost",\n'
            '   "dbtableprefix" => "",\n'
            '   "directory" => "'+os.path.join(datadir if datadir else path, 'data')+'",\n'
            '   );\n'
            '?>\n'
            )
        f.close()
        shell('chown http:http '+os.path.join(path, 'config', 'autoconfig.php'))

        # Make sure that the correct PHP settings are enabled
        phpctl.enable_mod('mysql', 'pdo_mysql', 'zip', 'gd',
            'iconv', 'openssl', 'xcache')
        
        # Make sure xcache has the correct settings, otherwise ownCloud breaks
        f = open('/etc/php/conf.d/xcache.ini', 'w')
        oc = ['extension=xcache.so\n',
            'xcache.size=64M\n',
            'xcache.var_size=64M\n',
            'xcache.admin.enable_auth = Off\n',
            'xcache.admin.user = "admin"\n',
            'xcache.admin.pass = "'+secret_key[8:24]+'"\n']
        f.writelines(oc)
        f.close()

        # Return an explicatory message
        if detect_architecture()[1] == 'Raspberry Pi':
            return ('ownCloud takes a long time to set up on the RPi. '
            'Once you open the page for the first time, it may take 5-10 '
            'minutes for the content to appear. Please do not refresh the '
            'page.')

    def pre_remove(self, name, path):
        datadir = ''
        dbname = name
        if os.path.exists(os.path.join(path, 'config', 'config.php')):
            f = open(os.path.join(path, 'config', 'config.php'), 'r')
            for line in f.readlines():
                if 'dbname' in line:
                    data = line.split('\'')[1::2]
                    dbname = data[1]
                elif 'datadirectory' in line:
                    data = line.split('\'')[1::2]
                    datadir = data[1]
            f.close()
        elif os.path.exists(os.path.join(path, 'config', 'autoconfig.php')):
            f = open(os.path.join(path, 'config', 'autoconfig.php'), 'r')
            for line in f.readlines():
                if 'dbname' in line:
                    data = line.split('\"')[1::2]
                    dbname = data[1]
                elif 'directory' in line:
                    data = line.split('\'')[1::2]
                    datadir = data[1]
            f.close()
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        dbase.remove(dbname, conn)
        dbase.usermod(dbname, 'del', '', conn)
        phpctl = apis.langassist(self.app).get_interface('PHP')
        phpctl.set_large_upload_size()
        if datadir:
            shutil.rmtree(datadir)
            phpctl.open_basedir('del', datadir)

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        # First, force SSL in ownCloud's config file
        if os.path.exists(os.path.join(path, 'config', 'config.php')):
            px = os.path.join(path, 'config', 'config.php')
        else:
            px = os.path.join(path, 'config', 'autoconfig.php')
        ic = open(px, 'r').readlines()
        f = open(px, 'w')
        oc = []
        found = False
        for l in ic:
            if '"forcessl" =>' in l:
                l = '"forcessl" => true,\n'
                oc.append(l)
                found = True
            else:
                oc.append(l)
        if found == False:
            for x in enumerate(oc):
                if '"dbhost" =>' in x[1]:
                    oc.insert(x[0] + 1, '"forcessl" => true,\n')
        f.writelines(oc)
        f.close()

        # Next, update the ca-certificates thing to include our cert
        # (if necessary)
        if not os.path.exists('/usr/share/ca-certificates'):
            try:
                os.makedirs('/usr/share/ca-certificates')
            except OSError, e:
                if e.errno == errno.EEXIST and os.path.isdir('/usr/share/ca-certificates'):
                    pass
                else:
                    raise
        shutil.copy(cfile, '/usr/share/ca-certificates/')
        fname = cfile.rstrip('/').split('/')[-1]
        ic = open('/etc/ca-certificates.conf', 'r').readlines()
        f = open('/etc/ca-certificates.conf', 'w')
        oc = []
        for l in ic:
            if l != fname+'\n':
                oc.append(l)
        oc.append(fname+'\n')
        f.writelines(oc)
        f.close()
        shell('update-ca-certificates')

    def ssl_disable(self, path):
        if os.path.exists(os.path.join(path, 'config', 'config.php')):
            px = os.path.join(path, 'config', 'config.php')
        else:
            px = os.path.join(path, 'config', 'autoconfig.php')
        ic = open(px, 'r').readlines()
        f = open(px, 'w')
        oc = []
        found = False
        for l in ic:
            if '"forcessl" =>' in l:
                l = '"forcessl" => false,\n'
                oc.append(l)
                found = True
            else:
                oc.append(l)
        if found == False:
            for x in enumerate(oc):
                if '"dbhost" =>' in x[1]:
                    oc.insert(x[0] + 1, '"forcessl" => false,\n')
        f.writelines(oc)
        f.close()

    def show_opts_add(self, ui):
        poi_sel = []
        for x in sorted(apis.poicontrol(self.app).get_pois(), key=lambda x: x.name):
            poi_sel.append(UI.SelectOption(text=x.name, value=x.path))
        ui.appendAll('oc-ddir', *poi_sel)
