from genesis.com import *
from genesis.apis import API

class Databases(API):

	class IDatabase(Interface):
		def add(self):
			pass

		def remove(self):
			pass

		def adduser(self):
			pass

		def deluser(self):
			pass

		def get_dbs(self):
			pass