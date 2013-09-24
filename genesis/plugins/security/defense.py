import ConfigParser
import os

from genesis.com import *
from genesis.api import *
from genesis import apis


class F2BConfigNotFound(Exception):
	def __str__(self):
		return ('The intrusion prevention config file could not be found, '
			'or the system (fail2ban) is not installed.')


class F2BManager(Plugin):
	abstract = True
	jailconf = '/etc/fail2ban/jail.conf'
	filters = '/etc/fail2ban/filter.d'

	def enable_jail(self, jailname):
		cfg = ConfigParser.SafeConfigParser()
		if cfg.read(self.jailconf) == []:
			raise F2BConfigNotFound()
		cfg.set(jailname, 'enabled', 'true')
		f = open(self.jailconf, 'w')
		cfg.write(f)
		f.close()

	def disable_jail(self, jailname):
		cfg = ConfigParser.SafeConfigParser()
		if cfg.read(self.jailconf) == []:
			raise F2BConfigNotFound()
		cfg.set(jailname, 'enabled', 'false')
		f = open(self.jailconf, 'w')
		cfg.write(f)
		f.close()

	def enable_all(self, obj):
		cfg = ConfigParser.SafeConfigParser()
		if cfg.read(self.jailconf) == []:
			raise F2BConfigNotFound()
		for jail in obj['f2b']:
			cfg.set(jail['name'], 'enabled', 'true')
		f = open(self.jailconf, 'w')
		cfg.write(f)
		f.close()

	def disable_all(self, obj):
		cfg = ConfigParser.SafeConfigParser()
		if cfg.read(self.jailconf) == []:
			raise F2BConfigNotFound()
		for jail in obj['f2b']:
			cfg.set(jail['name'], 'enabled', 'false')
		f = open(self.jailconf, 'w')
		cfg.write(f)
		f.close()

	def get_all(self):
		lst = []
		cfg = ConfigParser.SafeConfigParser()
		fcfg = ConfigParser.SafeConfigParser()
		if cfg.read(self.jailconf) == []:
			raise F2BConfigNotFound()
		for c in self.app.grab_plugins(ICategoryProvider):
			if hasattr(c, 'fail2ban'):
				lst.append({'name': c.text,
					'icon': c.iconfont,
					'f2b': c.fail2ban})
		for s in apis.webapps(self.app).get_apptypes():
			if hasattr(s, 'fail2ban'):
				lst.append({'name': s.name, 
					'icon': 'gen-earth',
					'f2b': s.fail2ban})
		for p in lst:
			for l in p['f2b']:
				if not 'custom' in l:
					jail_opts = cfg.items(l['name'])
					filter_name = cfg.get(l['name'], 'filter')
					fcfg.read([self.filters+'/common.conf', 
						self.filters+'/'+filter_name+'.conf'])
					filter_opts = fcfg.items('Definition')
					l['jail_opts'] = jail_opts
					l['filter_name'] = filter_name
					l['filter_opts'] = filter_opts
				else:
					if not l['name'] in cfg.sections():
						f = open(self.jailconf, 'w')
						for o in jail_opts:
							cfg.set(l['name'], o[0], o[1])
						cfg.write(f)
						f.close()
					if not os.path.exists(self.filters+'/'+filter_name+'.conf'):
						f = open(self.filters+'/'+filter_name+'.conf', 'w')
						fcfg = ConfigParser.SafeConfigParser()
						for o in filter_opts:
							fcfg.set(l['name'], o[0], o[1])
						fcfg.write(f)
						f.close()
		return lst
