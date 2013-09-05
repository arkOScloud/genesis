from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import hashlib
import os
import random
import urllib


class WordPress(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'WordPress'
	dpath = 'https://wordpress.org/latest.tar.gz'
	icon = 'gen-earth'
	services = [('MariaDB', 'mysqld'), ('PHP FastCGI', 'php-fpm')]
	php = True
	nomulti = True

	addtoblock = (
		'	location = /favicon.ico {\n'
		'		log_not_found off;\n'
		'		access_log off;\n'
		'	}\n'
		'\n'
		'	location = /robots.txt {\n'
		'		allow all;\n'
		'		log_not_found off;\n'
		'		access_log off;\n'
		'	}\n'
		'\n'
		'	location / {\n'
		'		try_files $uri $uri/ /index.php?$args;\n'
		'	}\n'
		'\n'
		'	location ~ \.php$ {\n'
		'		fastcgi_pass unix:/run/php-fpm/php-fpm.sock;\n'
		'		fastcgi_index index.php;\n'
		'		include fastcgi.conf;\n'
		'}\n'
		'\n'
		'	location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {\n'
		'		expires max;\n'
		'		log_not_found off;\n'
		'	}\n'
		)

	def pre_install(self, name, vars):
		pass

	def post_install(self, name, path, vars):
		# Get the database object, and determine proper values
		dbase = apis.databases(self.app).get_interface('MariaDB')
		if vars.getvalue('wp-dbname', '') == '':
			dbname = name
		else:
			dbname = vars.getvalue('wp-dbname')
		secret_key = hashlib.sha1(str(random.random())).hexdigest()
		if vars.getvalue('wp-dbpasswd', '') == '':
			passwd = secret_key[0:8]
		else:
			passwd = vars.getvalue('wp-dbpasswd')

		# Request a database and user to interact with it
		dbase.add(dbname)
		dbase.usermod(dbname, 'add', passwd)
		dbase.chperm(dbname, dbname, 'grant')

		# Use the WordPress key generators as first option
		# If connection fails, use the secret_key as fallback
		try:
			keysection = urllib.urlopen('https://api.wordpress.org/secret-key/1.1/salt/').read()
		except:
			keysection = ''
		if not 'define(\'AUTH_KEY' in keysection:
			keysection = (
				'define(\'AUTH_KEY\', \''+secret_key+'\');\n'
				'define(\'SECURE_AUTH_KEY\', \''+secret_key+'\');\n'
				'define(\'LOGGED_IN_KEY\', \''+secret_key+'\');\n'
				'define(\'NONCE_KEY\', \''+secret_key+'\');\n'
				)

		# Write a standard WordPress config file
		f = open(os.path.join(path, 'wp-config.php'), 'w')
		f.write('<?php\n'
				'define(\'DB_NAME\', \''+dbname+'\');\n'
				'define(\'DB_USER\', \''+dbname+'\');\n'
				'define(\'DB_PASSWORD\', \''+passwd+'\');\n'
				'define(\'DB_HOST\', \'localhost\');\n'
				'define(\'DB_CHARSET\', \'utf8\');\n'
				'define(\'SECRET_KEY\', \''+secret_key+'\');\n'
				'\n'
				'define(\'WP_CACHE\', true);\n'
				'\n'
				'/*\n'
				+keysection+
				'*/\n'
				'\n'
				'$table_prefix = \'wp_\';\n'
				'\n'
				'/** Absolute path to the WordPress directory. */\n'
				'if ( !defined(\'ABSPATH\') )\n'
				'	define(\'ABSPATH\', dirname(__FILE__) . \'/\');\n'
				'\n'
				'/** Sets up WordPress vars and included files. */\n'
				'require_once(ABSPATH . \'wp-settings.php\');\n'
			)
		f.close()

		# Make sure that the correct PHP settings are enabled
		shell('sed -i s/\;extension=mysql.so/extension=mysql.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=apc.so/extension=apc.so/g /etc/php/conf.d/apc.ini')

		# Finally, make sure that permissions are set so that Wordpress
		# can make adjustments and save plugins when need be.
		shell('chown -R http:http '+path)

	def pre_remove(self, name, path):
		f = open(os.path.join(path, 'wp-config.php'), 'r')
		for line in f.readlines():
			if 'DB_NAME' in line:
				data = line.split('\'')[1::2]
				dbname = data[1]
				break
		f.close()
		dbase = apis.databases(self.app).get_interface('MariaDB')
		dbase.remove(dbname)
		dbase.usermod(dbname, 'del', '')

	def post_remove(self, name):
		pass

	def get_info(self):
		return {
			'name': 'WordPress',
			'short': 'Open-source CMS and blogging platform',
			'long': ('WordPress started as just a blogging system, '
					'but has evolved to be used as full content management system '
					'and so much more through the thousands of plugins, widgets, '
					'and themes, WordPress is limited only by your imagination. '
					'(And tech chops.)'),
			'site': 'http://wordpress.org',
			'logo': True
		}
