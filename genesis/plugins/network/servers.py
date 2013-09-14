from genesis import apis
from genesis.api import *
from genesis.plugins.webapps.api import Webapps


class Server(object):
	id = ''
	name = ''
	icon = ''
	ports = []
	allow = ''

class ServerManager(apis.API):
	servers = []

	def __init__(self, app):
		self.app = app

	def add(self, id, name, icon='', ports=[], allow=0):
		s = Server()
		s.id = id
		s.name = name
		s.icon = icon
		s.ports = ports
		s.allow = allow
		self.servers.append(s)

	def update(self, id, name, icon='', ports=[], allow=0):
		s = self.get(id)
		s.icon = icon
		s.ports = ports
		s.allow = allow

	def get(self, id):
		slist = []
		for x in self.servers:
			if x.id == id:
				slist.append(x)
		return slist

	def get_all(self):
		return self.servers

	def scan_plugins(self):
		for c in self.app.grab_plugins(ICategoryProvider):
			for s in self.servers:
				if c.plugin_id == s.id and c.text == s.name:
					break
			else:
				if hasattr(c, 'ports'):
					self.add(c.plugin_id, c.text, c.iconfont, c.ports, 2)

	def scan_webapps(self):
		for x in self.servers:
			if x.id == 'webapps':
				self.servers.pop(x)
		for s in Webapps(self.app).get_sites():
			self.add('webapps', s['name'] + ' (' + s['type'] + ')',
				'gen-earth', [s['port']], 2)

	def remove(self, name):
		self.servers.pop(lambda x: x.name == name)
