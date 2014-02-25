from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, download
from genesis import apis
from api import Webapp

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
	def add(self, cat, name, wa, vars, enable=True):
		specialmsg = ''
		webapp = apis.webapps(self.app).get_interface(wa.wa_plugin)

		if not wa.dpath:
			ending = ''
		elif wa.dpath.endswith('.tar.gz'):
			ending = '.tar.gz'
		elif wa.dpath.endswith('.tar.bz2'):
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
		if wa.dpath:
			try:
				cat.put_statusmsg('Downloading webapp package...')
				download(wa.dpath, file=pkg_path, crit=True)
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
		if wa.wa_plugin == 'Website' and php == '1' and addtoblock:
			addtoblock.extend(x for x in webapp.phpblock)
		elif wa.wa_plugin == 'Website' and php == '1':
			addtoblock = webapp.phpblock

		# Setup the webapp and create an nginx serverblock
		try:
			w = Webapp()
			w.name = name
			w.stype = wa.wa_plugin
			w.path = target_path
			w.addr = vars.getvalue('addr', 'localhost')
			w.port = vars.getvalue('port', '80')
			w.php = True if wa.php is True or php is '1' else False
			self.nginx_add(site=w, 
				add=addtoblock if addtoblock else webapp.addtoblock, 
				)
		except Exception, e:
			raise PartialError('nginx serverblock couldn\'t be written - '+str(e))

		try:
			cat.put_statusmsg('Running post-install configuration...')
			specialmsg = webapp.post_install(name, target_path, vars)
		except Exception, e:
			shutil.rmtree(target_path, True)
			self.nginx_remove(w, False)
			raise InstallError('Webapp config - '+str(e))

		if enable is True:
			try:
				self.nginx_enable(w)
			except:
				raise ReloadError('nginx')
		if enable is True and wa.php is True:
			try:
				self.php_reload()
			except:
				raise ReloadError('PHP-FPM')

		# Make sure that nginx is enabled by default
		cat.app.get_backend(apis.services.IServiceManager).enable('nginx')

		cat.clr_statusmsg()

		if specialmsg:
			return specialmsg

	def add_reverse_proxy(self, name, path, addr, port):
		w = Webapp()
		w.name = name
		w.stype = 'ReverseProxy'
		w.path = path
		w.addr = addr
		w.port = port
		block = [
			nginx.Location('/admin/media/',
				nginx.Key('root', '/usr/lib/python2.7/site-packages/django/contrib')
			),
			nginx.Location('/',
				nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
				nginx.Key('proxy_set_header', 'Host $http_host'),
				nginx.Key('proxy_redirect', 'off'),
				nginx.If('(!-f $request_filename)',
					nginx.Key('proxy_pass', 'unix:%s'%os.path.join(path, 'gunicorn.sock'))
					nginx.Key('break', '')
				)
			)
		]
		self.nginx_add(w, addtoblock=block)
		self.nginx_enable(w)

	def remove(self, cat, site):
		if site.sclass != '' and site.stype != 'ReverseProxy':
			cat.put_statusmsg('Preparing for removal...')
			site.sclass.pre_remove(site.name, site.path)
		cat.put_statusmsg('Removing website...')
		if site.path.endswith('_site'):
			shutil.rmtree(site.path.split('/_site')[0])
		elif site.path.endswith('htdocs'):
			shutil.rmtree(site.path.split('/htdocs')[0])
		else:
			shutil.rmtree(site.path)
		self.nginx_remove(site)
		apis.webapps(self.app).cert_remove_notify(site.name,
			site.stype)
		if site.sclass != '' and site.stype != 'ReverseProxy':
			cat.put_statusmsg('Cleaning up...')
			site.sclass.post_remove(site.name)

		cat.clr_statusmsg()

	def nginx_add(self, site, add):
		if site.path == '':
			site.path = os.path.join('/srv/http/webapps/', site.name)
		c = nginx.Conf()
		c.add(nginx.Comment('GENESIS %s %s' % (site.stype, 'http://'+site.addr+':'+site.port)))
		s = nginx.Server(
			nginx.Key('listen', site.port),
			nginx.Key('server_name', site.addr),
			nginx.Key('root', site.path),
			nginx.Key('index', 'index.'+('php' if site.php else 'html'))
		)
		if add:
			s.add(*[x for x in add])
		c.add(s)
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', site.name))

	def nginx_edit(self, oldsite, site):
		# Update the nginx serverblock
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', oldsite.name))
		c.filter('Comment')[0].comment = 'GENESIS %s %s' % (site.stype, (('https://' if site.ssl else 'http://')+site.addr+':'+site.port))
		c.servers[0].filter('Key', 'listen')[0].value = site.port+' ssl' if site.ssl else site.port
		c.servers[0].filter('Key', 'server_name')[0].value = site.addr
		c.servers[0].filter('Key', 'root')[0].value = site.path
		c.servers[0].filter('Key', 'index')[0].value = 'index.php' if site.php else 'index.html'
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', oldsite.name))
		# If the name was changed, rename the folder and files
		if site.name != oldsite.name:
			if os.path.exists(os.path.join('/srv/http/webapps', site.name)):
				shutil.rmtree(os.path.join('/srv/http/webapps', site.name))
			shutil.move(os.path.join('/srv/http/webapps', oldsite.name), 
				os.path.join('/srv/http/webapps', site.name))
			shutil.move(os.path.join('/etc/nginx/sites-available', oldsite.name),
				os.path.join('/etc/nginx/sites-available', site.name))
			self.nginx_disable(oldsite, reload=False)
			self.nginx_enable(site)
		self.nginx_reload()

	def nginx_remove(self, site, reload=True):
		try:
			self.nginx_disable(site, reload)
		except:
			pass
		os.unlink(os.path.join('/etc/nginx/sites-available', site.name))

	def nginx_enable(self, site, reload=True):
		origin = os.path.join('/etc/nginx/sites-available', site.name)
		target = os.path.join('/etc/nginx/sites-enabled', site.name)
		if not os.path.exists(target):
			os.symlink(origin, target)
		if reload == True:
			self.nginx_reload()

	def nginx_disable(self, site, reload=True):
		os.unlink(os.path.join('/etc/nginx/sites-enabled', site.name))
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
		name, stype = data.name, data.stype
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
			c.servers[0].remove(*c.servers[0].filter('Key', 'ssl_certificate'))
		if c.servers[0].filter('Key', 'ssl_certificate_key'):
			c.servers[0].remove(*c.servers[0].filter('Key', 'ssl_certificate_key'))
		if c.servers[0].filter('Key', 'ssl_protocols'):
			c.servers[0].remove(*c.servers[0].filter('Key', 'ssl_protocols'))
		if c.servers[0].filter('Key', 'ssl_ciphers'):
			c.servers[0].remove(*c.servers[0].filter('Key', 'ssl_ciphers'))
		c.servers[0].add(
			nginx.Key('ssl_certificate', cpath),
			nginx.Key('ssl_certificate_key', kpath),
			nginx.Key('ssl_protocols', 'SSLv3 TLSv1 TLSv1.1 TLSv1.2'),
			nginx.Key('ssl_ciphers', 'HIGH:!aNULL:!MD5')
			)
		c.filter('Comment')[0].comment = 'GENESIS %s https://%s:%s' \
			% (stype, data.addr, port)
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_enable(
			os.path.join('/srv/http/webapps', name), cpath, kpath)

	def ssl_disable(self, data):
		name, stype = data.name, data.stype
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
			% (stype, data.addr, port)
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_disable(
			os.path.join('/srv/http/webapps', name))
