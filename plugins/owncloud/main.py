from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs, download

import hashlib
import errno
import os
import random
import shutil


class ownCloud(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'ownCloud'
	dpath = 'http://download.owncloud.org/community/owncloud-5.0.13.tar.bz2'
	icon = 'gen-cloud'
	dbengine = 'MariaDB'
	services = [('MariaDB', 'mysqld'), ('PHP FastCGI', 'php-fpm')]
	php = True
	nomulti = True
	ssl = True
	addtoblock = (
		'	error_page 403 = /core/templates/403.php;\n'
		'	error_page 404 = /core/templates/404.php;\n'
		'	client_max_body_size 10G;\n'
		'	fastcgi_buffers 64 4K;\n'
		'\n'
		'	rewrite ^/caldav(.*)$ /remote.php/caldav$1 redirect;\n'
		'	rewrite ^/carddav(.*)$ /remote.php/carddav$1 redirect;\n'
		'	rewrite ^/webdav(.*)$ /remote.php/webdav$1 redirect;\n'
		'\n'
        '	location = /robots.txt {\n'
        '		allow all;\n'
        '		log_not_found off;\n'
        '		access_log off;\n'
        '	}\n'
        '\n'
        '	location ~ ^/(data|config|\.ht|db_structure\.xml|README) {\n'
        '		deny all;\n'
        '	}\n'
        '\n'
        '	location / {\n'
        '		rewrite ^/.well-known/host-meta /public.php?service=host-meta last;\n'
        '		rewrite ^/.well-known/host-meta.json /public.php?service=host-meta-json last;\n'
        '		rewrite ^/.well-known/carddav /remote.php/carddav/ redirect;\n'
        '		rewrite ^/.well-known/caldav /remote.php/caldav/ redirect;\n'
        '		rewrite ^(/core/doc/[^\/]+/)$ $1/index.html;\n'
        '		try_files $uri $uri/ index.php;\n'
        '	}\n'
        '\n'
        '	location ~ ^(.+?\.php)(/.*)?$ {\n'
        '		try_files $1 = 404;\n'
        '		include fastcgi_params;\n'
        '		fastcgi_param SCRIPT_FILENAME $document_root$1;\n'
        '		fastcgi_param PATH_INFO $2;\n'
        '		fastcgi_pass unix:/run/php-fpm/php-fpm.sock;\n'
        '		fastcgi_read_timeout 900s;\n'
        '}\n'
        '\n'
        '	location ~* ^.+\.(jpg|jpeg|gif|bmp|ico|png|css|js|swf)$ {\n'
        '		expires 30d;\n'
        '		access_log off;\n'
        '	}\n'
        )

	def pre_install(self, name, vars):
		dbname = vars.getvalue('oc-dbname', '')
		if ' ' in dbname or '-' in dbname:
			raise Exception('Database name must not contain spaces or dashes')
		elif len(dbname) > 16:
			raise Exception('Database name must be shorter than 16 characters')
		elif vars.getvalue('oc-username', '') == '':
			raise Exception('Must choose an ownCloud username')
		elif vars.getvalue('oc-logpasswd', '') == '':
			raise Exception('Must choose an ownCloud password')

	def post_install(self, name, path, vars):
		dbase = apis.databases(self.app).get_interface('MariaDB')
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
		dbase.add(dbname)
		dbase.usermod(dbname, 'add', passwd)
		dbase.chperm(dbname, dbname, 'grant')

		# Set ownership as necessary
		os.makedirs(os.path.join(path, 'data'))
		shell('chown -R http:http '+os.path.join(path, 'apps'))
		shell('chown -R http:http '+os.path.join(path, 'data'))
		shell('chown -R http:http '+os.path.join(path, 'config'))

		# Create ownCloud automatic configuration file
		f = open(os.path.join(path, 'config', 'autoconfig.php'), 'w')
		f.write(
			'<?php\n'
			'	$AUTOCONFIG = array(\n'
			'	"adminlogin" => "'+username+'",\n'
			'	"adminpass" => "'+logpasswd+'",\n'
			'	"dbtype" => "mysql",\n'
			'	"dbname" => "'+dbname+'",\n'
			'	"dbuser" => "'+dbname+'",\n'
			'	"dbpass" => "'+passwd+'",\n'
			'	"dbhost" => "localhost",\n'
			'	"dbtableprefix" => "",\n'
			'	"directory" => "'+os.path.join(path, 'data')+'",\n'
			'	);\n'
			'?>\n'
			)
		f.close()
		shell('chown http:http '+os.path.join(path, 'config', 'autoconfig.php'))

		# Make sure that the correct PHP settings are enabled
		shell('sed -i s/\;extension=mysql.so/extension=mysql.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=zip.so/extension=zip.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=gd.so/extension=gd.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=iconv.so/extension=iconv.so/g /etc/php/php.ini')
		shell('sed -i s/\;extension=openssl.so/extension=openssl.so/g /etc/php/php.ini')
		
		# Make sure xcache has the correct settings, otherwise ownCloud breaks
		f = open('/etc/php/conf.d/xcache.ini', 'w')
		oc = ['extension=xcache.so\n',
			'xcache.admin.enable_auth = Off\n',
			'xcache.admin.user = "admin"\n',
			'xcache.admin.pass = "'+secret_key[8:24]+'"\n']
		f.writelines(oc)
		f.close()

		# Return an explicatory message
		return 'ownCloud takes a long time to set up on the RPi. Once you open the page for the first time, it may take 5-10 minutes for the content to appear. Please do not refresh the page.'

	def pre_remove(self, name, path):
		dbname = name
		if os.path.exists(os.path.join(path, 'config', 'config.php')):
			f = open(os.path.join(path, 'config', 'config.php'), 'r')
			for line in f.readlines():
				if 'dbname' in line:
					data = line.split('\'')[1::2]
					dbname = data[1]
					break
			f.close()
		elif os.path.exists(os.path.join(path, 'config', 'autoconfig.php')):
			f = open(os.path.join(path, 'config', 'autoconfig.php'), 'r')
			for line in f.readlines():
				if 'dbname' in line:
					data = line.split('\"')[1::2]
					dbname = data[1]
					break
			f.close()
		dbase = apis.databases(self.app).get_interface('MariaDB')
		dbase.remove(dbname)
		dbase.usermod(dbname, 'del', '')

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

	def get_info(self):
		return {
			'name': 'ownCloud',
			'short': 'Host your calendar, contacts, photos, files and more',
			'long': ('ownCloud gives you universal access to your files '
					'through a web interface or WebDAV. It also provides a '
					'platform to easily view & sync your contacts, '
					'calendars and bookmarks across all your devices and '
					'enables basic editing right on the web. Installation '
					'has minimal server requirements, doesn\'t need special '
					'permissions and is quick. ownCloud is extendable via a '
					'simple but powerful API for applications and plugins.'),
			'site': 'http://owncloud.org',
			'logo': True
		}
