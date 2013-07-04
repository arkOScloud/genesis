from genesis.com import *
from genesis import apis

class Databases(apis.API):
	def __init__(self, app):
		self.app = app

	class IDatabase(Interface):
		def add(self):
			pass

		def remove(self):
			pass

		def usermod(self):
			pass

		def chperm(self):
			pass

		def execute(self):
			pass

		def get_dbs(self):
			pass

		def get_users(self):
			pass

	def get_dbtypes(self):
		dblist = []
		for plugin in self.app.grab_plugins(apis.databases.IDatabase):
			dblist.append(plugin.name)
		return dblist

	def get_databases(self):
		dblist = []
		for plugin in self.app.grab_plugins(apis.databases.IDatabase):
			for item in plugin.get_dbs():
				dblist.append(item)
		return dblist

	def get_interface(self, name):
		interface = ''
		for plugin in self.app.grab_plugins(apis.databases.IDatabase):
			if plugin.__class__.__name__ == name:
				interface = plugin
		return interface

	def get_users(self):
		userlist = []
		for plugin in self.app.grab_plugins(apis.databases.IDatabase):
			if plugin.multiuser == True:
				for item in plugin.get_users():
					userlist.append(item)
		return userlist
