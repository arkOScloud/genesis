import nginx

from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import hashlib
import os
import random
import shutil


class Wallabag(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = [
        nginx.Location('~ /(db)',
            nginx.Key('deny', 'all'),
            nginx.Key('return', '404')
            ),
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
        nginx.Location('~ \.php$',
            nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
            nginx.Key('fastcgi_index', 'index.php'),
            nginx.Key('include', 'fastcgi.conf')
            ),
        nginx.Location('~* \.(js|css|png|jpg|jpeg|gif|ico)$',
            nginx.Key('expires', 'max'),
            nginx.Key('log_not_found', 'off')
            )
        ]

    def pre_install(self, name, vars):
        dbname = vars.getvalue('wb-dbname', '')
        dbpasswd = vars.getvalue('wb-dbpasswd', '')
        if dbname and dbpasswd:
            apis.databases(self.app).get_interface('MariaDB').validate(
                dbname, dbname, dbpasswd)
        elif dbname:
            raise Exception('You must enter a database password if you specify a database name!')
        elif dbpasswd:
            raise Exception('You must enter a database name if you specify a database password!')

    def post_install(self, name, path, vars):
        # Get the database object, and determine proper values
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        if vars.getvalue('wb-dbname', '') == '':
            dbname = name
        else:
            dbname = vars.getvalue('wb-dbname')
        secret_key = hashlib.sha1(str(random.random())).hexdigest()
        if vars.getvalue('wb-dbpasswd', '') == '':
            passwd = secret_key[0:8]
        else:
            passwd = vars.getvalue('wb-dbpasswd')

        # Request a database and user to interact with it
        dbase.add(dbname, conn)
        dbase.usermod(dbname, 'add', passwd, conn)
        dbase.chperm(dbname, dbname, 'grant', conn)

        # Write a standard Wallabag config file
        shutil.copy(os.path.join(path, 'inc/poche/config.inc.php.new'),
            os.path.join(path, 'inc/poche/config.inc.php'))
        ic = open(os.path.join(path, 'inc/poche/config.inc.php'), 'r').readlines()
        f = open(os.path.join(path, 'inc/poche/config.inc.php'), 'w')
        oc = []
        for l in ic:
            if 'define (\'SALT\'' in l:
                l = 'define (\'SALT\', \''+secret_key+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE\'' in l:
                l = 'define (\'STORAGE\', \'mysql\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_DB\'' in l:
                l = 'define (\'STORAGE_DB\', \''+dbname+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_USER\'' in l:
                l = 'define (\'STORAGE_USER\', \''+dbname+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_PASSWORD\'' in l:
                l = 'define (\'STORAGE_PASSWORD\', \''+passwd+'\');\n'
                oc.append(l)
            else:
                oc.append(l)
        f.writelines(oc)
        f.close()

        # Make sure that the correct PHP settings are enabled
        shell('sed -i s/\;extension=zip.so/extension=zip.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=openssl.so/extension=openssl.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=pdo_mysql.so/extension=pdo_mysql.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=mysql.so/extension=mysql.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=tidy.so/extension=tidy.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=phar.so/extension=phar.so/g /etc/php/php.ini')
        shell('sed -i s/\;extension=xcache.so/extension=xcache.so/g /etc/php/conf.d/xcache.ini')

        # Set up Composer and install the proper modules
        if not os.path.exists('/root/.composer'):
            os.mkdir('/root/.composer')
        ic = open('/etc/php/php.ini', 'r').readlines()
        f = open('/etc/php/php.ini', 'w')
        oc = []
        for l in ic:
            if 'open_basedir = ' in l and '/root/.composer' not in l:
                l = l.rstrip('\n') + ':/root/.composer\n'
                oc.append(l)
            else:
                oc.append(l)
        f.writelines(oc)
        f.close()
        shell('cd '+os.path.join(path)+'; curl -s http://getcomposer.org/installer | php')
        shell('cd '+os.path.join(path)+'; COMPOSER_HOME=\'/root/.composer\' php composer.phar install', stderr=True)

        # Finish setting up the database then delete the install folder
        dbase.execute(dbname, 
            open(os.path.join(path, 'install/mysql.sql')).read(), conn)
        shutil.rmtree(os.path.join(path, 'install'))

        # Finally, make sure that permissions are set so that Poche
        # can make adjustments and save plugins when need be.
        shell('chmod -R 755 '+os.path.join(path, 'assets/')+' '
            +os.path.join(path, 'cache/')+' '
            +os.path.join(path, 'db/'))
        shell('chown -R http:http '+path)

    def pre_remove(self, name, path):
        f = open(os.path.join(path, 'inc/poche/config.inc.php'), 'r')
        for line in f.readlines():
            if 'STORAGE_DB' in line:
                data = line.split('\'')[1::2]
                dbname = data[1]
                break
        f.close()
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        dbase.remove(dbname, conn)
        dbase.usermod(dbname, 'del', '', conn)

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass
