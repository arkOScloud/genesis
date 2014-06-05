from genesis import apis
from genesis.com import *
from genesis.api import *
from genesis.plugmgr import PluginLoader

from api import *


class Server(object):
	server_id = ''
	plugin_id = ''
	name = ''
	icon = ''
	ports = []


class ServerManager(Plugin):
	abstract = True
	servers = []

	def add(self, plugin_id, server_id, name, icon='', ports=[]):
		s = Server()
		s.server_id = server_id
		s.plugin_id = plugin_id
		s.name = name
		s.icon = icon
		s.ports = ports
		self.servers.append(s)
		return s

	def update(self, old_id, new_id, name, icon='', ports=[]):
		s = self.get(old_id)[0]
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

	def get_by_plugin(self, id):
		slist = []
		for x in self.servers:
			if x.plugin_id == id:
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

	def get_ranges(self):
		ranges = []
		nc = self.app.get_backend(INetworkConfig)
		for x in nc.interfaces:
			i = nc.interfaces[x]
			r = nc.get_ip(i.name)
			if '127.0.0.1' in r or '0.0.0.0' in r:
				continue
			if not '/' in r:
			    ri = r
			    rr = '32'
			else:
				ri, rr = r.split('/')
			ri = ri.split('.')
			ri[3] = '0'
			ri = ".".join(ri)
			r = ri + '/' + rr
			ranges.append(r)
		return ranges

	def scan_plugins(self):
		lst = PluginLoader.list_plugins()
		for c in lst:
			if hasattr(lst[c], 'services'):
				for s in self.servers:
					if lst[c].id == s.plugin_id:
						break
				else:
					for p in lst[c].services:
						try:
							if p['ports'] != []:
								self.add(lst[c].id, p['binary'], p['name'], 
									lst[c].icon, p['ports'])
						except IndexError:
							pass

	def scan_webapps(self):
		for x in enumerate(self.servers):
			if x[1].plugin_id == 'webapps':
				self.servers.pop(x[0])
		for s in apis.webapps(self.app).get_sites():
			self.add('webapps', s.name, s.name + ' (' + s.stype + ')',
				'gen-earth', [('tcp', s.port)])

	def remove(self, id):
		for s in enumerate(self.servers):
			if s[1].server_id == id:
				self.servers.pop(s[0])

	def remove_by_plugin(self, id):
		for s in enumerate(self.servers):
			if s[1].plugin_id == id:
				self.servers.pop(s[0])
