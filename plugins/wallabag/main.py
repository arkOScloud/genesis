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
        if vars.getvalue('wb-username', '') == '':
            raise Exception('Must choose a Wallabag username')
        elif vars.getvalue('wb-passwd', '') == '':
            raise Exception('Must choose a Wallabag password')
        elif '"' in vars.getvalue('wb-passwd', '') or "'" in vars.getvalue('wb-passwd', ''):
            raise Exception('Your Wallabag password must not include quotes')

    def post_install(self, name, path, vars, dbinfo={}):
        phpctl = apis.langassist(self.app).get_interface('PHP')
        secret_key = hashlib.sha1(str(random.random())).hexdigest()
        dbengine = 'mysql' if dbinfo['engine'] == 'MariaDB' else 'sqlite'

        username = vars.getvalue("wb-username", "wallabag")
        passwd = vars.getvalue("wb-passwd", "wallabag") + username + secret_key
        passwd = hashlib.sha1(passwd).hexdigest()

        # Write a standard Wallabag config file
        shutil.copy(os.path.join(path, 'inc/poche/config.inc.default.php'),
            os.path.join(path, 'inc/poche/config.inc.php'))
        ic = open(os.path.join(path, 'inc/poche/config.inc.php'), 'r').readlines()
        f = open(os.path.join(path, 'inc/poche/config.inc.php'), 'w')
        oc = []
        for l in ic:
            if 'define (\'SALT\'' in l:
                l = '@define (\'SALT\', \''+secret_key+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE\'' in l:
                l = '@define (\'STORAGE\', \''+dbengine+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_SQLITE\'' in l and dbengine == 'sqlite':
                l = '@define (\'STORAGE_SQLITE\', \'/var/lib/sqlite3/'+dbinfo['name']+'.db\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_DB\'' in l and dbengine == 'mysql':
                l = '@define (\'STORAGE_DB\', \''+dbinfo['name']+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_USER\'' in l and dbengine == 'mysql':
                l = '@define (\'STORAGE_USER\', \''+dbinfo['user']+'\');\n'
                oc.append(l)
            elif 'define (\'STORAGE_PASSWORD\'' in l and dbengine == 'mysql':
                l = '@define (\'STORAGE_PASSWORD\', \''+dbinfo['passwd']+'\');\n'
                oc.append(l)
            else:
                oc.append(l)
        f.writelines(oc)
        f.close()

        # Make sure that the correct PHP settings are enabled
        phpctl.enable_mod('mysql' if dbengine == 'mysql' else 'sqlite3', 
            'pdo_mysql' if dbengine == 'mysql' else 'pdo_sqlite', 
            'zip', 'tidy', 'xcache', 'openssl')

        # Set up Composer and install the proper modules
        phpctl.composer_install(path)

        # Set up the database then delete the install folder
        if dbengine == 'mysql':
            dbase = apis.databases(self.app).get_interface(dbinfo['engine'])
            conn = apis.databases(self.app).get_dbconn(dbinfo['engine'])
            dbase.execute(dbinfo['name'], 
                open(os.path.join(path, 'install/mysql.sql')).read(), conn)
            dbase.execute(dbinfo['name'],
                "INSERT INTO users (username, password, name, email) VALUES ('%s', '%s', '%s', '');" % (username, passwd, username),
                conn, commit=True)
            lid = int(conn.insert_id())
            dbase.execute(dbinfo['name'],
                "INSERT INTO users_config (user_id, name, value) VALUES (%s, 'pager', '10');" % lid,
                conn, commit=True)
            dbase.execute(dbinfo['name'],
                "INSERT INTO users_config (user_id, name, value) VALUES (%s, 'language', 'en_EN.UTF8');" % lid,
                conn, commit=True)
        else:
            dbase = apis.databases(self.app).get_interface(dbinfo['engine'])
            dbase.chkpath()
            shutil.copy(os.path.join(path, 'install/poche.sqlite'), '/var/lib/sqlite3/%s.db' % dbinfo['name'])
            phpctl.open_basedir('add', '/var/lib/sqlite3')
            shell('chown :sqlite3 /var/lib/sqlite3/%s.db' % dbinfo['name'])
            dbase.execute(dbinfo['name'],
                "INSERT INTO users (username, password, name, email) VALUES ('%s', '%s', '%s', '');" % (username, passwd, username))
            dbase.execute(dbinfo['name'],
                "INSERT INTO users_config (user_id, name, value) VALUES (1, 'pager', '10');")
            dbase.execute(dbinfo['name'],
                "INSERT INTO users_config (user_id, name, value) VALUES (1, 'language', 'en_EN.UTF8');")
        shutil.rmtree(os.path.join(path, 'install'))

        # Finally, make sure that permissions are set so that Wallabag
        # can make adjustments and save plugins when need be.
        shell('chmod -R 755 '+os.path.join(path, 'assets/')+' '
            +os.path.join(path, 'cache/')+' '
            +os.path.join(path, 'db/'))
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
        # General update procedure
        shell('tar xzf %s -C %s --strip 1' % (pkg, path))
        for x in os.listdir(os.path.join(path, 'cache')):
            if os.path.isdir(os.path.join(path, 'cache', x)):
                shutil.rmtree(os.path.join(path, 'cache', x))
            else:
                os.unlink(os.path.join(path, 'cache', x))
        shutil.rmtree(os.path.join(path, 'install'))
        shell('chmod -R 755 '+os.path.join(path, 'assets/')+' '
            +os.path.join(path, 'cache/')+' '
            +os.path.join(path, 'db/'))
        shell('chown -R http:http '+path)
