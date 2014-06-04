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


class WordPress(Plugin):
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
		pass

	def post_install(self, name, path, vars, dbinfo={}):
		phpctl = apis.langassist(self.app).get_interface('PHP')
		secret_key = hashlib.sha1(str(random.random())).hexdigest()

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
				'define(\'DB_NAME\', \''+dbinfo['name']+'\');\n'
				'define(\'DB_USER\', \''+dbinfo['user']+'\');\n'
				'define(\'DB_PASSWORD\', \''+dbinfo['passwd']+'\');\n'
				'define(\'DB_HOST\', \'localhost\');\n'
				'define(\'DB_CHARSET\', \'utf8\');\n'
				'define(\'SECRET_KEY\', \''+secret_key+'\');\n'
				'\n'
				'define(\'WP_CACHE\', true);\n'
				'define(\'FORCE_SSL_ADMIN\', false);\n'
				'\n'
				+keysection+
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
		phpctl.enable_mod('mysql', 'xcache')

		# Finally, make sure that permissions are set so that Wordpress
		# can make adjustments and save plugins when need be.
		shell('chown -R http:http '+path)

	def pre_remove(self, site):
		pass

	def post_remove(self, site):
		pass

	def ssl_enable(self, path, cfile, kfile):
		ic = open(os.path.join(path, 'wp-config.php'), 'r').readlines()
		f = open(os.path.join(path, 'wp-config.php'), 'w')
		oc = []
		found = False
		for l in ic:
			if 'define(\'FORCE_SSL_ADMIN\'' in l:
				l = 'define(\'FORCE_SSL_ADMIN\', false);\n'
				oc.append(l)
				found = True
			else:
				oc.append(l)
		if found == False:
			oc.append('define(\'FORCE_SSL_ADMIN\', true);\n')
		f.writelines(oc)
		f.close()

	def ssl_disable(self, path):
		ic = open(os.path.join(path, 'wp-config.php'), 'r').readlines()
		f = open(os.path.join(path, 'wp-config.php'), 'w')
		oc = []
		found = False
		for l in ic:
			if 'define(\'FORCE_SSL_ADMIN\'' in l:
				l = 'define(\'FORCE_SSL_ADMIN\', false);\n'
				oc.append(l)
				found = True
			else:
				oc.append(l)
		if found == False:
			oc.append('define(\'FORCE_SSL_ADMIN\', false);\n')
		f.writelines(oc)
		f.close()
