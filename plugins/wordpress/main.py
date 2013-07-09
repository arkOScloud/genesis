from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs, download

import ast
import hashlib
import os
import random
import shutil


class WordPress(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'WordPress'
	dpath = 'https://wordpress.org/latest.tar.gz'
	icon = 'gen-earth'

	def install(self, name):
		download(dpath, file='/tmp/wordpress.tar.gz')
		shell('tar xzf '+os.path.join(path, 'wordpress.zip')
			+' -C '+os.path.join('/var/webapps/wordpress', name)
			+' --strip 1')
		dbase = apis.databases(self.app).get_interface('MariaDB')
		dbase.add(name)
		secret_key = hashlib.sha1(str(random.random())).hexdigest()
		passwd = secret_key[0:8]
		f = open(os.path.join('/var/webapps/wordpress', name, 'wp-config.php'), 'w')
		f.write('<?php\n'
				'define(\'DB_NAME\', \''+name+'\');\n'
				'define(\'DB_USER\', \''+name+'\');\n'
				'define(\'DB_PASSWORD\', \''+passwd+'\');\n'
				'define(\'DB_HOST\', \'localhost\');\n'
				'define(\'SECRET_KEY\', \''+secret_key+'\');\n'
 				'\n'
				'define(\'WP_CACHE\', true);\n'
 				'\n'
				'/*\n'
				'define(\'AUTH_KEY\', \''+secret_key+'\');\n'
				'define(\'SECURE_AUTH_KEY\', \''+secret_key+'\');\n'
				'define(\'LOGGED_IN_KEY\', \''+secret_key+'\');\n'
				'define(\'NONCE_KEY\', \''+secret_key+'\');\n'
				'*/'
				'\n'
				'$table_prefix = \'wp_\';\n'
				'\n'
				'/** Absolute path to the WordPress directory. */\n'
				'if ( !defined(\'ABSPATH\') )\n'
				'define(\'ABSPATH\', dirname(__FILE__) . \'/\');\n'
				'\n'
				'/** Pull in the config information */\n'
				'require_once(ABSPATH . \'wp-info.php\');\n'
				'require_once(ABSPATH . \'wp-overrides.php\');\n'
				'\n'
				'/** Sets up WordPress vars and included files. */\n'
				'require_once(ABSPATH . \'wp-settings.php\');\n'
			)
		dbase.usermod(name, 'add', passwd)
		dbase.chperm(name, name, 'grant')

	def remove(self, name):
		dbase = apis.databases(self.app).get_interface('MariaDB')
		dbase.remove(name)
		dbase.usermod(name, 'del', '')
		shutil.rmtree(os.path.join('/var/webapps/wordpress', name))

	def get_sites(self):
		sitelist = []
		if not os.path.isdir('/var/webapps/wordpress'):
			os.makedirs('/var/webapps/wordpress')
		for thing in os.walk('/var/webapps/wordpress').next()[1]:
			path = os.path.join('/var/webapps/wordpress', thing)
			if os.path.exists(os.path.join(path, '.genesis')):
				f = open(os.path.join(path, '.genesis'), 'r')
				try:
					data = ast.literal_eval(f.read())
					sitelist.append(data)
				except:
					pass
				f.close()
		return sitelist

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
