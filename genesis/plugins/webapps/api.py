from genesis.com import *
from genesis import apis

import ConfigParser
import glob
import nginx
import os
import re


class Webapps(apis.API):
	def __init__(self, app):
		self.app = app

	class IWebapp(Interface):
		name = ''
		dpath = ''
		icon = 'gen-earth'
		php = False
		nomulti = False
		addtoblock = ''
		ssl = False

		def pre_install(self, name, vars):
			pass

		def post_install(self, name, path, vars):
			pass

		def pre_remove(self, name, path):
			pass

		def post_remove(self, name):
			pass

		def get_info(self):
			pass

		def ssl_enable(self, path, cfile, kfile):
			pass

		def ssl_disable(self, path):
			pass

	def get_apptypes(self):
		applist = []
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			applist.append(plugin)
		return applist

	def get_sites(self):
		applist = []
		if not os.path.exists('/etc/nginx/sites-available'):
			os.makedirs('/etc/nginx/sites-available')
		if not os.path.exists('/etc/nginx/sites-enabled'):
			os.makedirs('/etc/nginx/sites-enabled')

		for site in os.listdir('/etc/nginx/sites-available'):
			# Set default values and regexs to use
			addr = False
			port = '80'
			stype = 'Unknown'
			path = os.path.join('/etc/nginx/sites-available', site)
			rtype = re.compile('GENESIS ((?:[a-z][a-z]+))', flags=re.IGNORECASE)
			rport = re.compile('(\\d+)\s*(.*?)')

			# Get actual values
			try:
				c = nginx.loadf(path)
				stype = re.match(rtype, c.filter('Comment')[0]).group(1)
				port, ssl = re.match(rport, c.servers[0].filter('Key', 'listen')[0].value).group(1, 2)
				addr = c.servers[0].filter('Key', 'server_name')[0].value
				path = c.servers[0].filter('Key', 'root')[0].value
				php = True if 'php' in c.servers[0].filter('Key', 'index')[0].value else False
			except IndexError:
				pass

			if os.path.exists(os.path.join('/etc/nginx/sites-enabled', site)):
				enabled = True
			else:
				enabled = False

			cls = self.get_interface(stype)
			if hasattr(cls, 'ssl'):
				ssl_able = cls.ssl
			else:
				ssl_able = False

			# Create dict of values
			applist.append({
					'name': site,
					'type': stype,
					'ssl': (True if ssl == 'ssl' else False),
					'ssl_able': ssl_able,
					'addr': addr, 
					'port': port,
					'path': path, 
					'php': php,
					'class': cls,
					'enabled': enabled
				})
			f.close()
		return applist

	def get_interface(self, name):
		interface = ''
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			if plugin.__class__.__name__ == name:
				interface = plugin
		return interface

	def cert_remove_notify(self, name, stype):
		# Called by webapp when removed.
		# Removes the associated entry from gcinfo tracker file
		# Placed here for now to avoid awkward circular import
		try:
			cfg = ConfigParser.ConfigParser()
			for x in glob.glob('/etc/ssl/certs/genesis/*.gcinfo'):
				cfg.read(x)
				alist = []
				write = False
				for i in cfg.get('cert', 'assign').split('\n'):
					if i != (name+' ('+stype+')'):
						alist.append(i)
					else:
						write = True
				if write == True:
					cfg.set('cert', 'assign', '\n'.join(alist))
					cfg.write(open(x, 'w'))
		except:
			pass
