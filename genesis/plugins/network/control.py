from genesis.com import *
from genesis.api import *
from genesis.plugins.security.firewall import RuleManager, FWMonitor

from servers import *


class NetworkControl(Plugin):
	# Convenience functions for routine synchronized ops
	def session_start(self):
		servers = ServerManager()
		servers.add('genesis', 'genesis', 'Genesis', 'gen-arkos-round',
			[('tcp', self.app.gconfig.get('genesis', 'bind_port'))])
		servers.scan_plugins()
		servers.scan_webapps()
		RuleManager().scan_servers()
		FWMonitor().regen(servers.get_ranges())

	def session_stop(self):
		pass

	def refresh(self):
		servers = ServerManager()
		servers.scan_plugins()
		RuleManager.scan_servers()
		FWMonitor.regen(servers.get_ranges())

	def remove(self, id):
		servers = ServerManager()
		RuleManager.remove_by_plugin(id)
		servers.remove_by_plugin(id)
		FWMonitor.regen(servers.get_ranges())
