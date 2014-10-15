from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs, download
from genesis import apis
from api import Webapp

import ConfigParser
import hashlib
import nginx
import os
import random
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
	def __init__(self, cause, action="Install"):
		self.action = action
		self.cause = cause

	def __str__(self):
		return '%s successful, but %s restart failed. Check your configs' % (self.action, self.cause)


class WebappControl(Plugin):
	def add(self, cat, wa, vars, dbinfo={}, enable=True):
		specialmsg = ''
		name = vars.getvalue('name', '').lower()
		webapp = apis.webapps(self.app).get_interface(wa.wa_plugin)

		if not wa.dpath:
			ending = ''
		elif wa.dpath.endswith('.tar.gz'):
			ending = '.tar.gz'
		elif wa.dpath.endswith('.tgz'):
			ending = '.tgz'
		elif wa.dpath.endswith('.tar.bz2'):
			ending = '.tar.bz2'
		elif wa.dpath.endswith('.zip'):
			ending = '.zip'
		elif wa.dpath.endswith('.git'):
			ending = '.git'
		else:
			raise InstallError('Only GIT repos, gzip, bzip, and zip packages supported for now')

		# Run webapp preconfig, if any
		try:
			cat.statusmsg('Running pre-install configuration...')
			webapp.pre_install(name, vars)
		except Exception, e:
			raise InstallError('Webapp config - '+str(e))

		if dbinfo:
			pwd = hashlib.sha1(str(random.random())).hexdigest()[0:16]
			dbinfo['name'] = dbinfo['name'] if dbinfo['name'] else name
			dbinfo['user'] = dbinfo['user'] if dbinfo['user'] else name
			dbinfo['passwd'] = dbinfo['passwd'] if dbinfo['passwd'] else pwd
			try:
				db = apis.databases(cat.app)
				dbase = db.get_interface(dbinfo['engine'])
				conn = db.get_dbconn(dbinfo['engine'])
				dbase.add(dbinfo['name'], conn)
				dbase.usermod(dbinfo['user'], 'add', dbinfo['passwd'], conn)
				dbase.chperm(dbinfo['name'], dbinfo['user'], 'grant', conn)
			except Exception, e:
				raise InstallError('Databases could not be created - %s' % str(e))

		# Make sure the target directory exists, but is empty
		# Testing for sites with the same name should have happened by now
		target_path = os.path.join('/srv/http/webapps', name)
		pkg_path = '/tmp/'+name+ending
		if os.path.isdir(target_path):
			shutil.rmtree(target_path)
		os.makedirs(target_path)

		# Download and extract the source package
		if wa.dpath and ending == '.git':
			status = shell_cs('git clone %s %s'%(wa.dpath,target_path), stderr=True)
			if status[0] >= 1:
				raise InstallError(status[1])
		elif wa.dpath:
			try:
				cat.statusmsg('Downloading webapp package...')
				download(wa.dpath, file=pkg_path, crit=True)
			except Exception, e:
				raise InstallError('Couldn\'t download - %s' % str(e))

			if ending in ['.tar.gz', '.tgz', '.tar.bz2']:
				extract_cmd = 'tar '
				extract_cmd += 'xzf' if ending in ['.tar.gz', '.tgz'] else 'xjf'
				extract_cmd += ' /tmp/%s -C %s --strip 1' % (name+ending, target_path)
			else:
				extract_cmd = 'unzip -d %s /tmp/%s' % (target_path, name+ending)

			status = shell_cs(extract_cmd, stderr=True)
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
			w.version = wa.version.rsplit('-', 1)[0] if wa.website_updates else None
			w.dbengine = dbinfo['engine'] if dbinfo else None
			w.dbname = dbinfo['name'] if dbinfo else None
			w.dbuser = dbinfo['user'] if dbinfo else None
			self.nginx_add(site=w, 
				add=addtoblock if addtoblock else webapp.addtoblock, 
				)
		except Exception, e:
			raise PartialError('nginx serverblock couldn\'t be written - '+str(e))

		try:
			cat.statusmsg('Running post-install configuration...')
			specialmsg = webapp.post_install(name, target_path, vars, dbinfo)
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

		# Add the new path to tracked points of interest (POIs)
		apis.poicontrol(self.app).add(name, 'website', target_path, 'webapps',
            webapp.plugin_info.icon, False)

		if specialmsg:
			return specialmsg

	def add_reverse_proxy(self, name, path, addr, port, block):
		w = Webapp()
		w.name = name
		w.stype = 'ReverseProxy'
		w.path = path
		w.addr = addr
		w.port = port
		w.dbengine = None
		w.dbname = None
		w.dbuser = None
		if not block:
			block = [
				nginx.Location('/admin/media/',
					nginx.Key('root', '/usr/lib/python2.7/site-packages/django/contrib')
				),
				nginx.Location('/',
					nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
					nginx.Key('proxy_set_header', 'Host $http_host'),
					nginx.Key('proxy_redirect', 'off'),
					nginx.If('(!-f $request_filename)',
						nginx.Key('proxy_pass', 'unix:%s'%os.path.join(path, 'gunicorn.sock')),
						nginx.Key('break', '')
					)
				)
			]
		self.nginx_add(w, block)
		self.nginx_enable(w)

	def update(self, cat, wa, site):
		if not wa.dpath:
			ending = ''
		elif wa.dpath.endswith('.tar.gz'):
			ending = '.tar.gz'
		elif wa.dpath.endswith('.tgz'):
			ending = '.tgz'
		elif wa.dpath.endswith('.tar.bz2'):
			ending = '.tar.bz2'
		elif wa.dpath.endswith('.zip'):
			ending = '.zip'
		elif wa.dpath.endswith('.git'):
			ending = '.git'
		else:
			raise InstallError('Only GIT repos, gzip, bzip, and zip packages supported for now')

		cat.statusmsg('Downloading package...')
		if wa.dpath and ending == '.git':
			pkg_path = wa.dpath 
		elif wa.dpath:
			pkg_path = os.path.join('/tmp', site.name+ending)
			try:
				download(wa.dpath, file=pkg_path, crit=True)
			except Exception, e:
				raise InstallError('Couldn\'t update - %s' % str(e))
		cat.statusmsg('Updating site...')
		try:
			site.sclass.update(site.path, pkg_path, site.version)
		except Exception, e:
			raise InstallError('Couldn\'t update - %s' % str(e))
		finally:
			site.version = wa.version.rsplit('-', 1)[0]
			c = ConfigParser.RawConfigParser()
			c.read(os.path.join('/etc/nginx/sites-available', '.'+site.name+'.ginf'))
			c.set('website', 'version', site.version)
			c.write(open(os.path.join('/etc/nginx/sites-available', '.'+site.name+'.ginf'), 'w'))
			cat.put_message('success', '%s updated successfully' % site.name)
		if pkg_path:
			os.unlink(pkg_path)

	def remove(self, cat, site):
		if site.sclass and site.stype != 'ReverseProxy':
			cat.statusmsg('Preparing for removal...')
			site.sclass.pre_remove(site)
		cat.statusmsg('Removing website...')
		if site.stype != 'ReverseProxy':
			if site.path.endswith('_site'):
				shutil.rmtree(site.path.split('/_site')[0])
			elif site.path.endswith('htdocs'):
				shutil.rmtree(site.path.split('/htdocs')[0])
			elif os.path.islink(site.path):
				os.unlink(site.path)
			else:
				shutil.rmtree(site.path)
			if hasattr(site, 'dbengine') and site.dbengine:
				try:
					db = apis.databases(cat.app)
					dbase = db.get_interface(site.dbengine)
					conn = db.get_dbconn(site.dbengine)
					dbase.remove(site.dbname, conn)
					dbase.usermod(site.dbuser, 'del', '', conn)
				except Exception, e:
					cat.put_message('warn', 'Databases could not be removed - maybe they are gone already? Please check manually.')
		self.nginx_remove(site)
		if site.sclass and site.stype != 'ReverseProxy':
			cat.statusmsg('Cleaning up...')
			apis.poicontrol(self.app).drop_by_path(site.path)
			site.sclass.post_remove(site)

	def nginx_add(self, site, add):
		if site.path == '':
			site.path = os.path.join('/srv/http/webapps/', site.name)
		c = nginx.Conf()
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
		# Write configuration file with info Genesis needs to know the site
		f = open(os.path.join('/etc/nginx/sites-available', '.'+site.name+'.ginf'), 'w')
		c = ConfigParser.SafeConfigParser()
		c.add_section('website')
		c.set('website', 'name', site.name)
		c.set('website', 'stype', site.stype)
		c.set('website', 'ssl', '')
		c.set('website', 'version', site.version if site.version else 'None')
		c.set('website', 'dbengine', site.dbengine if site.dbengine else '')
		c.set('website', 'dbname', site.dbname if site.dbname else '')
		c.set('website', 'dbuser', site.dbuser if site.dbuser else '')
		c.write(f)
		f.close()

	def nginx_edit(self, oldsite, site):
		# Update the nginx serverblock
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', oldsite.name))
		s = c.servers[0]
		if oldsite.ssl and oldsite.port == '443':
			for x in c.servers:
				if x.filter('Key', 'listen')[0].value == '443 ssl':
					s = x
			if site.port != '443':
				for x in c.servers:
					if not 'ssl' in x.filter('Key', 'listen')[0].value \
					and x.filter('key', 'return'):
						c.remove(x)
		elif site.port == '443':
			c.add(nginx.Server(
				nginx.Key('listen', '80'),
				nginx.Key('server_name', site.addr),
				nginx.Key('return', '301 https://%s$request_uri'%site.addr)
			))
		# If the name was changed, rename the folder and files
		if site.name != oldsite.name:
			if site.path.endswith('_site'):
				site.path = os.path.join('/srv/http/webapps', site.name, '_site')
			elif site.path.endswith('htdocs'):
				site.path = os.path.join('/srv/http/webapps', site.name, 'htdocs')
			else:
				site.path = os.path.join('/srv/http/webapps', site.name)
			g = ConfigParser.SafeConfigParser()
			g.read(os.path.join('/etc/nginx/sites-available', '.'+oldsite.name+'.ginf'))
			g.set('website', 'name', site.name)
			g.write(open(os.path.join('/etc/nginx/sites-available', '.'+site.name+'.ginf'), 'w'))
			os.unlink(os.path.join('/etc/nginx/sites-available', '.'+oldsite.name+'.ginf'))
			if os.path.exists(os.path.join('/srv/http/webapps', site.name)):
				shutil.rmtree(os.path.join('/srv/http/webapps', site.name))
			shutil.move(os.path.join('/srv/http/webapps', oldsite.name), 
				os.path.join('/srv/http/webapps', site.name))
			shutil.move(os.path.join('/etc/nginx/sites-available', oldsite.name),
				os.path.join('/etc/nginx/sites-available', site.name))
			self.nginx_disable(oldsite, reload=False)
			self.nginx_enable(site, reload=False)
		s.filter('Key', 'listen')[0].value = site.port+' ssl' if site.ssl else site.port
		s.filter('Key', 'server_name')[0].value = site.addr
		s.filter('Key', 'root')[0].value = site.path
		s.filter('Key', 'index')[0].value = 'index.php' if site.php else 'index.html'
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', oldsite.name))
		self.nginx_reload()

	def nginx_remove(self, site, reload=True):
		try:
			self.nginx_disable(site, reload)
		except:
			pass
		os.unlink(os.path.join('/etc/nginx/sites-available', site.name))
		os.unlink(os.path.join('/etc/nginx/sites-available', '.'+site.name+'.ginf'))

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
			raise ReloadError('nginx failed to reload.', "Edit")

	def php_enable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\tinclude \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

	def php_disable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\t#include \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

	def php_reload(self):
		status = shell_cs('systemctl restart php-fpm')
		if status[0] >= 1:
			raise Exception('PHP FastCGI failed to reload.')

	def ssl_enable(self, data, cname, cpath, kpath):
		# If no cipher preferences set, use the default ones
		# As per Mozilla recommendations, but substituting 3DES for RC4
		from genesis.plugins.certificates.backend import CertControl
		ciphers = ':'.join([
			'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES128-GCM-SHA256',
			'ECDHE-RSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-AES256-GCM-SHA384',
			'kEDH+AESGCM', 'ECDHE-RSA-AES128-SHA256', 
			'ECDHE-ECDSA-AES128-SHA256', 'ECDHE-RSA-AES128-SHA', 
			'ECDHE-ECDSA-AES128-SHA', 'ECDHE-RSA-AES256-SHA384',
			'ECDHE-ECDSA-AES256-SHA384', 'ECDHE-RSA-AES256-SHA', 
			'ECDHE-ECDSA-AES256-SHA', 'DHE-RSA-AES128-SHA256',
			'DHE-RSA-AES128-SHA', 'DHE-RSA-AES256-SHA256', 
			'DHE-DSS-AES256-SHA', 'AES128-GCM-SHA256', 'AES256-GCM-SHA384',
			'ECDHE-RSA-DES-CBC3-SHA', 'ECDHE-ECDSA-DES-CBC3-SHA',
			'EDH-RSA-DES-CBC3-SHA', 'EDH-DSS-DES-CBC3-SHA', 
			'DES-CBC3-SHA', 'HIGH', '!aNULL', '!eNULL', '!EXPORT', '!DES',
			'!RC4', '!MD5', '!PSK'
			])
		cfg = self.app.get_config(CertControl(self.app))
		if hasattr(cfg, 'ciphers') and cfg.ciphers:
			ciphers = cfg.ciphers
		elif hasattr(cfg, 'ciphers'):
			cfg.ciphers = ciphers
			cfg.save()

		name, stype = data.name, data.stype
		port = '443'
		c = nginx.loadf('/etc/nginx/sites-available/'+name)
		s = c.servers[0]
		l = s.filter('Key', 'listen')[0]
		if l.value == '80':
			l.value = '443 ssl'
			port = '443'
			c.add(nginx.Server(
				nginx.Key('listen', '80'),
				nginx.Key('server_name', data.addr),
				nginx.Key('return', '301 https://%s$request_uri'%data.addr)
			))
			for x in c.servers:
				if x.filter('Key', 'listen')[0].value == '443 ssl':
					s = x
					break
		else:
			port = l.value.split(' ssl')[0]
			l.value = l.value.split(' ssl')[0] + ' ssl'
		for x in s.all():
			if type(x) == nginx.Key and x.name.startswith('ssl_'):
				s.remove(x)
		s.add(
			nginx.Key('ssl_certificate', cpath),
			nginx.Key('ssl_certificate_key', kpath),
			nginx.Key('ssl_protocols', 'TLSv1 TLSv1.1 TLSv1.2'),
			nginx.Key('ssl_ciphers', ciphers),
			nginx.Key('ssl_session_timeout', '5m'),
			nginx.Key('ssl_prefer_server_ciphers', 'on'),
			nginx.Key('ssl_session_cache', 'shared:SSL:50m'),
			)
		g = ConfigParser.SafeConfigParser()
		g.read(os.path.join('/etc/nginx/sites-available', '.'+name+'.ginf'))
		g.set('website', 'ssl', cname)
		g.write(open(os.path.join('/etc/nginx/sites-available', '.'+name+'.ginf'), 'w'))
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_enable(
			os.path.join('/srv/http/webapps', name), cpath, kpath)

	def ssl_disable(self, data):
		name, stype = data.name, data.stype
		port = '80'
		s = None
		c = nginx.loadf('/etc/nginx/sites-available/'+name)
		if len(c.servers) > 1:
			for x in c.servers:
				if not 'ssl' in x.filter('Key', 'listen')[0].value \
				and x.filter('key', 'return'):
					c.remove(x)
					break
		s = c.servers[0]
		l = s.filter('Key', 'listen')[0]
		if l.value == '443 ssl':
			l.value = '80'
			port = '80'
		else:
			l.value = l.value.rstrip(' ssl')
			port = l.value
		s.remove(*[x for x in s.filter('Key') if x.name.startswith('ssl_')])
		g = ConfigParser.SafeConfigParser()
		g.read(os.path.join('/etc/nginx/sites-available', '.'+name+'.ginf'))
		g.set('website', 'ssl', '')
		g.write(open(os.path.join('/etc/nginx/sites-available', '.'+name+'.ginf'), 'w'))
		nginx.dumpf(c, '/etc/nginx/sites-available/'+name)
		apis.webapps(self.app).get_interface(stype).ssl_disable(
			os.path.join('/srv/http/webapps', name))
