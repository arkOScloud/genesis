from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, download
from genesis import apis

import os
import re
import shutil

import nginxparser


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

		# Setup the webapp and create an nginx serverblock
		try:
			self.nginx_add(
				name=name, 
				stype=webapp.name, 
				path=target_path, 
				addr=vars.getvalue('addr', 'localhost'), 
				port=vars.getvalue('port', '80'), 
				add=(addtoblock if addtoblock is not '' else webapp.addtoblock), 
				php=(True if webapp.php is True or php is '1' else False)
				)
		except Exception, e:
			raise PartialError('nginx serverblock couldn\'t be written - '+str(e))

		try:
			cat.put_statusmsg('Running post-install configuration...')
			specialmsg = webapp.post_install(name, target_path, vars)
		except Exception, e:
			raise InstallError('Webapp config - '+str(e))

		if webapp.name == 'Website' and php == '1':
			addtoblock = webapp.phpblock + '\n' + addtoblock

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
		if site['class'] != '':
			cat.put_statusmsg('Cleaning up...')
			site['class'].post_remove(site['name'])
		cat.clr_statusmsg()

	def nginx_add(self, name, stype, path, addr, port, add='', php=False):
		# TODO update this to use nginxparser
		if path == '':
			path = os.path.join('/srv/http/webapps/', name)
		f = open('/etc/nginx/sites-available/'+name, 'w')
		f.write(
			'# GENESIS '+stype+' http://'+addr+':'+port+'\n'
			'server {\n'
			'   listen '+port+';\n'
			'   server_name '+addr+';\n'
			'   root '+path+';\n'
			'   index index.'+('php' if php else 'html')+';\n'
			+(add if add is not '' else '')+'\n'
			'}\n'
			)
		f.close()

	def nginx_edit(self, origname, name, stype, path, addr, port, ssl, php=False):
		# TODO update this to use nginxparser
		if path.endswith('_site'):
			path = re.sub('/', '\/', os.path.join('/srv/http/webapps/', name, '_site'))
		else:
			path = re.sub('/', '\/', os.path.join('/srv/http/webapps/', name))
		shell('sed -i "s/.*GENESIS.*/# GENESIS %s %s/" /etc/nginx/sites-available/%s' 
			% (stype, (('https:\/\/' if ssl else 'http:\/\/')+addr+':'+port), origname))	
		shell('sed -i "s/.*listen .*/\tlisten %s\;/" /etc/nginx/sites-available/%s' % ((port+' ssl' if ssl else port), origname))
		shell('sed -i "s/.*server_name .*/\tserver_name %s\;/" /etc/nginx/sites-available/%s' % (addr, origname))
		shell('sed -i "s/.*root .*/\troot %s\;/" /etc/nginx/sites-available/%s' % (path, origname))
		shell('sed -i "s/.*index index.*/\tindex index.%s\;/" /etc/nginx/sites-available/%s' % ('php' if php else 'html', origname))
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
		n = nginxparser.loads(
			open('/etc/nginx/sites-available/'+name, 'r').read())
		port = '443'
		for l in n:
			if l[0] == ['server']:
				for x in l[1]:
					if x[0] == 'listen':
						if x[1] == '80':
							x[1] = '443 ssl'
							port = '443'
						else:
							port = x[1]
							x[1] = x[1] + ' ssl'
				l[1].append(['ssl_certificate', cpath])
				l[1].append(['ssl_certificate_key', kpath])
				l[1].append(['ssl_protocols', 'TLSv1 TLSv1.1 TLSv1.2'])
				l[1].append(['ssl_ciphers', 'HIGH:!aNULL:!MD5'])
		comline = '# GENESIS '+stype+' https://'+data['addr']+':'+port+'\n'
		open('/etc/nginx/sites-available/'+name, 'w').write(
			comline+nginxparser.dumps(n))
		apis.webapps(self.app).get_interface(stype).ssl_enable(
			os.path.join('/srv/http/webapps', name), cpath, kpath)
		self.nginx_reload()

	def ssl_disable(self, data):
		name, stype = data['name'], data['type']
		n = nginxparser.loads(
			open('/etc/nginx/sites-available/'+name, 'r').read())
		port = '80'
		# Three passes - list loop bug omits entries on some systems 
		for l in n:
			if l[0] == ['server']:
				for x in l[1]:
					if x[0] == 'listen':
						if x[1] == '443 ssl':
							x[1] = '80'
							port = '80'
							print True
						else:
							x[1] = x[1].rstrip(' ssl')
							print x[1]
							port = x[1]
					elif x[0] == 'ssl_certificate':
						l[1].remove(x)
					elif x[0] == 'ssl_certificate_key':
						l[1].remove(x)
					elif x[0] == 'ssl_protocols':
						l[1].remove(x)
					elif x[0] == 'ssl_ciphers':
						l[1].remove(x)
		for l in n:
			if l[0] == ['server']:
				for x in l[1]:
					if x[0] == 'ssl_certificate':
						l[1].remove(x)
					elif x[0] == 'ssl_certificate_key':
						l[1].remove(x)
					elif x[0] == 'ssl_protocols':
						l[1].remove(x)
					elif x[0] == 'ssl_ciphers':
						l[1].remove(x)
		for l in n:
			if l[0] == ['server']:
				for x in l[1]:
					if x[0] == 'ssl_certificate':
						l[1].remove(x)
					elif x[0] == 'ssl_certificate_key':
						l[1].remove(x)
					elif x[0] == 'ssl_protocols':
						l[1].remove(x)
					elif x[0] == 'ssl_ciphers':
						l[1].remove(x)
		comline = '# GENESIS '+stype+' http://'+data['addr']+':'+port+'\n'
		open('/etc/nginx/sites-available/'+name, 'w').write(
			comline+nginxparser.dumps(n))
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

	addtoblock = ''

	phpblock = (
		'	location ~ \.php$ {\n'
		'		fastcgi_pass unix:/run/php-fpm/php-fpm.sock;\n'
		'		fastcgi_index index.php;\n'
		'		include fastcgi.conf;\n'
		'	}\n'
		)

	def pre_install(self, name, vars):
		if vars.getvalue('ws-dbsel', 'None') == 'None':
			if vars.getvalue('ws-dbname', '') != '':
				raise Exception('Must choose a database type if you want to create one')
			if vars.getvalue('ws-dbpass', '') != '':
				raise Exception('Must choose a database type if you want to create one')
		if vars.getvalue('ws-dbsel', 'None') != 'None':
			if vars.getvalue('ws-dbname', '') == '':
				raise Exception('Must choose a database name if you want to create one')
			if vars.getvalue('ws-dbpass', '') == '':
				raise Exception('Must choose a database password if you want to create one')

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
