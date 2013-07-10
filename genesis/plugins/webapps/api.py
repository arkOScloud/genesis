from genesis.com import *
from genesis import apis
from genesis.utils import shell, shell_cs

import os


class Webapps(apis.API):
	def __init__(self, app):
		self.app = app

	class IWebapp(Interface):
		name = ''
		dpath = ''
		icon = 'gen-earth'
		php = False
		nomulti = False

		def install(self, name):
			pass

		def remove(self, name):
			pass

		def get_info(self):
			pass

	def get_apptypes(self):
		applist = []
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			applist.append(plugin.name)
		return applist

	def get_sites(self):
		applist = []
		for site in os.listdir('/etc/nginx/sites-available'):
			f = open(os.path.join('/etc/nginx/sites-available', site), 'r')
			data = f.readline()
			if 'GENESIS' in data:
				stype = data[2:].split()
				stype = stype[1]
			else:
				stype = 'Unknown'
			if os.path.exists(os.path.join('/etc/nginx/sites-enabled', site)):
				enabled = True
			else:
				enabled = False
			applist.append({
					'name': site,
					'type': stype,
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

	def php_enable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\tinclude \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

	def php_disable(self):
		shell('sed -i "s/.*include \/etc\/nginx\/php.conf.*/\t#include \/etc\/nginx\/php.conf;/" /etc/nginx/nginx.conf')

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

	def nginx_remove(self, sitename, reload=True):
		try:
			self.nginx_disable(sitename, reload)
		except:
			pass
		os.unlink(os.path.join('/etc/nginx/sites-available', sitename))

	def nginx_reload(self):
		status = shell_cs('systemctl restart nginx')
		if status[0] >= 1:
			raise Exception(status[1])
