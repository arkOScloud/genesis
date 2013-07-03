from genesis.com import *
from genesis import apis

class Databases(apis.API):

	class IDatabase(Interface):
		def add(self):
			pass

		def remove(self):
			pass

		def adduser(self):
			pass

		def deluser(self):
			pass

		def execute(self):
			pass

		def get_dbs(self):
			pass

class DBOps(apis.API):
	def __init__(self, app):
		self.app = app

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

	def get_dbcls(self, name):
		dbcls = ''
		for plugin in self.app.grab_plugins(apis.databases.IDatabase):
			if plugin.__class__.__name__ == name:
				dbcls = plugin
		return dbcls
