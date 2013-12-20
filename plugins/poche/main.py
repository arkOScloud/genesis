from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import hashlib
import os
import random
import shutil


class Poche(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'Poche'
	dpath = 'https://github.com/inthepoche/poche/archive/1.2.0.tar.gz'
	icon = 'gen-earth'
	dbengine = 'MariaDB'
	services = [('MariaDB', 'mysqld'), ('PHP FastCGI', 'php-fpm')]
	php = True
	nomulti = True
	ssl = True

	addtoblock = (
		'	location ~ /(db) {\n'
		'		deny all;\n'
		'		return 404;\n'
		'	}\n'
		'\n'
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
		'	}\n'
		'\n'
		'	location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {\n'
		'		expires max;\n'
		'		log_not_found off;\n'
		'	}\n'
		)

	def pre_install(self, name, vars):
		dbname = vars.getvalue('po-dbname', '')
		if ' ' in dbname or '-' in dbname:
			raise Exception('Database name must not contain spaces or dashes')
		elif len(dbname) > 16:
			raise Exception('Database name must be shorter than 16 characters')

	def post_install(self, name, path, vars):
		# Get the database object, and determine proper values
		dbase = apis.databases(self.app).get_interface('MariaDB')
		if vars.getvalue('po-dbname', '') == '':
			dbname = name
		else:
			dbname = vars.getvalue('po-dbname')
		secret_key = hashlib.sha1(str(random.random())).hexdigest()
		if vars.getvalue('wp-dbpasswd', '') == '':
			passwd = secret_key[0:8]
		else:
			passwd = vars.getvalue('po-dbpasswd')

		# Request a database and user to interact with it
		dbase.add(dbname)
		dbase.usermod(dbname, 'add', passwd)
		dbase.chperm(dbname, dbname, 'grant')

		# Write a standard Poche config file
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
		shell('sed -i s/\;extension=mysql.so/extension=mysql.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=tidy.so/extension=tidy.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=phar.so/extension=phar.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=xcache.so/extension=xcache.so/g /etc/php/conf.d/xcache.ini')

		# Set up Composer and install the proper modules
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
		shell('cd '+os.path.join(path)+'; php composer.phar install', stderr=True)

		# Finish setting up the database then delete the install folder
		shell('mysql '+dbname+' < '+os.path.join(path, 'install/mysql.sql'))
		shutil.rmtree(os.path.join(path, 'install'))

		# Finally, make sure that permissions are set so that Poche
		# can make adjustments and save plugins when need be.
		shell('chmod -R 777 http:http '+os.path.join(path, 'assets/')+' '
			+os.path.join(path, 'cache/')+' '
			+os.path.join(path, 'db/'))

	def pre_remove(self, name, path):
		f = open(os.path.join(path, 'inc/poche/config.inc.php'), 'r')
		for line in f.readlines():
			if 'STORAGE_DB' in line:
				data = line.split('\'')[1::2]
				dbname = data[1]
				break
		f.close()
		dbase = apis.databases(self.app).get_interface('MariaDB')
		dbase.remove(dbname)
		dbase.usermod(dbname, 'del', '')

	def post_remove(self, name):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def get_info(self):
		return {
			'name': 'Poche',
			'short': 'The self hosted read-it-later app',
			'long': ('Poche is a self hostable read-it-later app. '
				'Unlike to other services, poche is free and open source.'),
			'site': 'http://www.inthepoche.com',
			'logo': True
		}
