from genesis import apis
from genesis.api import *
from genesis.plugins.webapps.api import Webapps


class Server(object):
	server_id = ''
	plugin_id = ''
	name = ''
	icon = ''
	ports = []


class ServerManager(apis.API):
	servers = []

	def __init__(self, app):
		self.app = app

	def add(self, server_id, plugin_id, name, icon='', ports=[]):
		s = Server()
		s.server_id = server_id
		s.plugin_id = plugin_id
		s.name = name
		s.icon = icon
		s.ports = ports
		self.servers.append(s)

	def update(self, old_id, new_id, name, icon='', ports=[]):
		s = self.get(old_id)
		s.server_id = new_id
		s.name = name
		s.icon = icon
		s.ports = ports

	def get(self, id):
		slist = []
		for x in self.servers:
			if x.server_id == id:
				slist.append(x)
		return slist

	def get_by_port(self, port):
		slist = []
		for x in self.servers:
			if port in x.ports[1]:
				slist.append(x)
		return slist

	def get_all(self):
		return self.servers

	def scan_plugins(self):
		for c in self.app.grab_plugins(ICategoryProvider):
			if hasattr(c, 'services'):
				for s in self.servers:
					if c.plugin_id == s.plugin_id and c.server_id == s.server_id:
						break
				else:
					for p in c.services:
						try:
							if p[2] != []:
								self.add(p[1], c.plugin_id, p[0], 
									c.iconfont, p[2])
						except IndexError:
							pass

	def scan_webapps(self):
		for x in self.servers:
			if x.plugin_id == 'webapps':
				self.servers.pop(x)
		for s in Webapps(self.app).get_sites():
			self.add(s['name'], 'webapps', s['name'] + ' (' + s['type'] + ')',
				'gen-earth', [s['port']])

	def remove(self, id):
		self.servers.pop(lambda x: x.server_id == id)
