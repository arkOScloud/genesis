from genesis.com import *
from genesis import apis

class Webapps(apis.API):
	def __init__(self, app):
		self.app = app

	class IWebapp(Interface):
		name = ''
		dpath = ''

		def install(self, package):
			pass

		def remove(self):
			pass

		def get_sites(self):
			pass

	def get_apptypes(self):
		applist = []
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			applist.append(plugin.name)
		return applist

	def get_sites(self):
		applist = []
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			for item in plugin.get_sites():
				applist.append(item)
		return applist

	def get_interface(self, name):
		interface = ''
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			if plugin.__class__.__name__ == name:
				interface = plugin
		return interface
