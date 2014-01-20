from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, download
from genesis import apis

import nginx
import os
import re
import shutil


class InstallError(Exception):
	def __init__(self, cause):
		self.cause = cause

	def __str__(self):
		return 'Installation failed: %s' % self.cause

class PartialError(Exception):
	def __init__(self, cause):
		self.cause = cause

	def __str__(self):
		return 'Installation successful, but %s' % self.cause

class ReloadError(Exception):
	def __init__(self, cause):
		self.cause = cause

	def __str__(self):
		return 'Installation successful, but %s restart failed. Check your configs' % self.cause


class WebappControl(Plugin):
	def add(self, cat, name, webapp, vars, enable=True):
		specialmsg = ''

		if webapp.dpath is None:
			ending = ''
		elif webapp.dpath.endswith('.tar.gz'):
			ending = '.tar.gz'
		elif webapp.dpath.endswith('.tar.bz2'):
			ending = '.tar.bz2'
		else:
			raise InstallError('Only gzip and bzip packages supported for now')

		# Run webapp preconfig, if any
		try:
			cat.put_statusmsg('Running pre-install configuration...')
			webapp.pre_install(name, vars)
		except Exception, e:
			raise InstallError('Webapp config - '+str(e))

		# Make sure the target directory exists, but is empty
		# Testing for sites with the same name should have happened by now
		target_path = os.path.join('/srv/http/webapps', name)
		pkg_path = '/tmp/'+name+ending
		if os.path.isdir(target_path):
			shutil.rmtree(target_path)
		os.makedirs(target_path)

		# Download and extract the source package
		if webapp.dpath is not None:
			try:
				cat.put_statusmsg('Downloading webapp package...')
				download(webapp.dpath, file=pkg_path)
			except Exception, e:
				raise InstallError('Couldn\'t download - %s' % str(e))
			status = shell_cs('tar '
				+('xzf' if ending is '.tar.gz' else 'xjf')
				+' /tmp/'+name+ending+' -C '
				+target_path+' --strip 1', stderr=True)
			if status[0] >= 1:
				raise InstallError(status[1])
			os.remove(pkg_path)

		php = vars.getvalue('php', '')
		addtoblock = vars.getvalue('addtoblock', '')

		if addtoblock:
			addtoblock = nginx.loads(addtoblock, False)
		else:
			addtoblock = []
		if webapp.name == 'Website' and php == '1' and addtoblock:
			addtoblock.extend(x for x in webapp.phpblock)

		# Setup the webapp and create an nginx serverblock
		try:
			self.nginx_add(
				name=name, 
				stype=webapp.name, 
				path=target_path, 
				addr=vars.getvalue('addr', 'localhost'), 
				port=vars.getvalue('port', '80'), 
				add=(addtoblock if addtoblock else webapp.addtoblock), 
				php=(True if webapp.php is True or php is '1' else False)
				)
		except Exception, e:
			raise PartialError('nginx serverblock couldn\'t be written - '+str(e))

		try:
			cat.put_statusmsg('Running post-install configuration...')
			specialmsg = webapp.post_install(name, target_path, vars)
		except Exception, e:
			shutil.rmtree(target_path, True)
			self.nginx_remove(name, False)
			raise InstallError('Webapp config - '+str(e))

		if enable is True:
			try:
				self.nginx_enable(name)
			except:
				raise ReloadError('nginx')
		if enable is True and webapp.php is True:
			try:
				self.php_enable()
				self.php_reload()
			except:
				raise ReloadError('PHP-FPM')

		# Make sure that nginx is enabled by default
		cat.app.get_backend(apis.services.IServiceManager).enable('nginx')

		cat.clr_statusmsg()

		if specialmsg:
			return specialmsg

	def remove(self, cat, site):
		if site['class'] != '':
			cat.put_statusmsg('Preparing for removal...')
			site['class'].pre_remove(site['name'], site['path'])
		cat.put_statusmsg('Removing website...')
		if site['path'].endswith('_site'):
			shutil.rmtree(site['path'].rstrip('/_site'))
		else:
			shutil.rmtree(site['path'])
		self.nginx_remove(site['name'])
		apis.webapps(self.app).cert_remove_notify(site['name'],
			site['type'])
		if site['class'] != '':
			cat.put_statusmsg('Cleaning up...')
			site['class'].post_remove(site['name'])

		cat.clr_statusmsg()

	def nginx_add(self, name, stype, path, addr, port, add='', php=False):
		if path == '':
			path = os.path.join('/srv/http/webapps/', name)
		c = nginx.Conf()
		c.add(nginx.Comment('GENESIS %s %s' % (stype, 'http://'+addr+':'+port)))
		s = nginx.Server(
			nginx.Key('listen', port),
			nginx.Key('server_name', addr),
			nginx.Key('root', path),
			nginx.Key('index', 'index.'+('php' if php else 'html'))
		)
		if add:
			s.add(*[x for x in add])
		c.add(s)
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)

	def nginx_edit(self, origname, name, stype, path, addr, port, ssl, php=False):
		# Update the nginx serverblock
		if path.endswith('_site'):
			path = re.sub('/', '\/', os.path.join('/srv/http/webapps/', name, '_site'))
		else:
			path = re.sub('/', '\/', os.path.join('/srv/http/webapps/', name))
		c = nginx.loadf('/etc/nginx/sites-available/'+name)
		c.filter('Comment')[0].comment = 'GENESIS %s %s' % (stype, (('https://' if ssl else 'http://')+addr+':'+port))
		c.servers[0].filter('Key', 'listen')[0].value = port+' ssl' if ssl else port
		c.servers[0].filter('Key', 'server_name')[0].value = addr
		c.servers[0].filter('Key', 'root')[0].value = path
		c.servers[0].filter('Key', 'index')[0].value = 'index.php' if php else 'index.html'
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		# If the name was changed, rename the folder and files
		if name != origname:
			if os.path.exists(os.path.join('/srv/http/webapps', name)):
				shutil.rmtree(os.path.join('/srv/http/webapps', name))
			shutil.move(os.path.join('/srv/http/webapps', origname), 
				os.path.join('/srv/http/webapps', name))
			shutil.move(os.path.join('/etc/nginx/sites-available', origname),
				os.path.join('/etc/nginx/sites-available', name))
			self.nginx_disable(origname, reload=False)
			self.nginx_enable(name)
		self.nginx_reload()

	def nginx_remove(self, sitename, reload=True):
		try:
			self.nginx_disable(sitename, reload)
		except:
			pass
		os.unlink(os.path.join('/etc/nginx/sites-available', sitename))

	def nginx_enable(self, sitename, reload=True):
		origin = os.path.join('/etc/nginx/sites-available', sitename)
		target = os.path.join('/etc/nginx/sites-enabled', sitename)
		if not os.path.exists(target):
			os.symlink(origin, target)
		if reload == True:
			self.nginx_reload()

	def nginx_disable(self, sitename, reload=True):
		os.unlink(os.path.join('/etc/nginx/sites-enabled', sitename))
		if reload == True:
			self.nginx_reload()

	def nginx_reload(self):
		status = shell_cs('systemctl restart nginx')
		if status[0] >= 1:
			raise Exception('nginx failed to reload.')

	def php_enable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\tinclude \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

	def php_disable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\t#include \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

	def php_reload(self):
		status = shell_cs('systemctl restart php-fpm')
		if status[0] >= 1:
			raise Exception('nginx failed to reload.')

	def ssl_enable(self, data, cpath, kpath):
		name, stype = data['name'], data['type']
		port = '443'
		c = nginx.loadf('/etc/nginx/sites-available/'+name)
		l = c.servers[0].filter('Key', 'listen')[0]
		if l.value == '80':
			l.value = '443 ssl'
			port = '443'
		else:
			port = l.value.split(' ssl')[0]
			l.value = l.value.split(' ssl')[0] + ' ssl'
		if c.servers[0].filter('Key', 'ssl_certificate'):
			c.servers[0].remove(c.servers[0].filter('Key', 'ssl_certificate'))
		if c.servers[0].filter('Key', 'ssl_certificate_key'):
			c.servers[0].remove(c.servers[0].filter('Key', 'ssl_certificate_key'))
		if c.servers[0].filter('Key', 'ssl_protocols'):
			c.servers[0].remove(c.servers[0].filter('Key', 'ssl_protocols'))
		if c.servers[0].filter('Key', 'ssl_ciphers'):
			c.servers[0].remove(c.servers[0].filter('Key', 'ssl_ciphers'))
		c.servers[0].add(
			nginx.Key('ssl_certificate', cpath),
			nginx.Key('ssl_certificate_key', kpath),
			nginx.Key('ssl_protocols', 'SSLv3 TLSv1 TLSv1.1 TLSv1.2'),
			nginx.Key('ssl_ciphers', 'HIGH:!aNULL:!MD5')
			)
		c.filter('Comment')[0].comment = 'GENESIS %s https://%s:%s' \
			% (stype, data['addr'], port)
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_enable(
			os.path.join('/srv/http/webapps', name), cpath, kpath)
		self.nginx_reload()

	def ssl_disable(self, data):
		name, stype = data['name'], data['type']
		port = '80'
		c = nginx.loadf('/etc/nginx/sites-available/'+name)
		l = c.servers[0].filter('Key', 'listen')[0]
		if l.value == '443 ssl':
			l.value = '80'
			port = '80'
		else:
			l.value = l.value.rstrip(' ssl')
			port = l.value
		c.servers[0].remove(
			c.servers[0].filter('Key', 'ssl_certificate')[0],
			c.servers[0].filter('Key', 'ssl_certificate_key')[0],
			c.servers[0].filter('Key', 'ssl_protocols')[0],
			c.servers[0].filter('Key', 'ssl_ciphers')[0]
			)
		c.filter('Comment')[0].comment = 'GENESIS %s http://%s:%s' \
			% (stype, data['addr'], port)
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_disable(
			os.path.join('/srv/http/webapps', name))
		self.nginx_reload()

class Website(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'Website'
	dpath = None
	icon = 'gen-earth'
	sort = 'bottom'
	php = False
	nomulti = False
	ssl = True

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
		# Create a database if the user wants one
		if vars.getvalue('ws-dbsel', 'None') != 'None':
			dbtype = vars.getvalue('ws-dbsel', '')
			dbname = vars.getvalue('ws-dbname', '')
			passwd = vars.getvalue('ws-dbpass', '')
			dbase = apis.databases(self.app).get_interface(dbtype)
			dbase.add(dbname)
			dbase.usermod(dbname, 'add', passwd)
			dbase.chperm(dbname, dbname, 'grant')
			shell('sed -i s/\;extension=mysql.so/extension=mysql.so/g /etc/php/php.ini')

		# Write a basic index file showing that we are here
		if vars.getvalue('php', '0') == '1':
			php = True
		else:
			php = False
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
			shell('sed -i s/\;extension=xcache.so/extension=xcache.so/g /etc/php/conf.d/xcache.ini')

	def pre_remove(self, name, path):
		pass

	def post_remove(self, name):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def get_info(self):
		return {
			'name': 'Website',
			'short': 'Upload your own HTML/PHP files',
			'long': ('Create a custom website with your own HTML or PHP '
					'files.'),
			'site': None,
			'logo': False
		}
