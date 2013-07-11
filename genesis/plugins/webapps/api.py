from genesis.com import *
from genesis import apis

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
		addtoblock = ''

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
				ldata = data[2:].split()
				stype = ldata[1]
				addr = ldata[2]
			else:
				addr = False
				stype = 'Unknown'
			if os.path.exists(os.path.join('/etc/nginx/sites-enabled', site)):
				enabled = True
			else:
				enabled = False
			applist.append({
					'name': site,
					'type': stype,
					'addr': addr,
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
