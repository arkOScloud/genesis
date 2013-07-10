from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import download


class WebAppsPlugin(CategoryPlugin):
	text = 'Websites'
	iconfont = 'gen-earth'
	folder = 'servers'

	def on_init(self):
		self.waops = apis.webapps(self.app)
		self.sites = sorted(self.waops.get_sites(), 
			key=lambda st: st['name'])
		self.apptypes = sorted(self.waops.get_apptypes())
		if not self._current:
			self._current = self.apptypes[0]

	def on_session_start(self):
		self._add = None
		self._setup = None

	def get_ui(self):
		ui = self.app.inflate('webapps:main')
		t = ui.find('list')

		for s in self.sites:
			t.append(UI.DTR(
				UI.Iconfont(iconfont="gen-earth"),
				UI.Label(text=s['name']),
				UI.Label(text=s['type']),
				UI.HContainer(
					UI.TipIcon(
						iconfont='gen-minus-circle' if s['enabled'] else 'gen-checkmark-circle',
						id=('disable/' if s['enabled'] else 'enable/') + str(self.sites.index(s)),
						text='Disable' if s['enabled'] else 'Enable'
					),
					UI.TipIcon(
						iconfont='gen-tools',
						id='config/' + str(self.sites.index(s)),
						text='Configure'
					),
					UI.TipIcon(
						iconfont='gen-cancel-circle',
						id='drop/' + str(self.sites.index(s)),
						text='Delete',
						warning='Delete site %s? This action is irreversible'%s['name']
						)
					),
				))

		provs = ui.find('provs')

		for apptype in self.apptypes:
			provs.append(
					UI.ListItem(
						UI.Label(text=apptype),
						id=apptype,
						active=apptype==self._current
					)
				)

		info = self.waops.get_interface(self._current).get_info()
		if info['logo'] is True:
			ui.find('logo').set('file', '/dl/'+info['name'].lower()+'/logo.png')
		ui.find('appname').set('text', info['name'])
		ui.find('short').set('text', info['short'])
		ui.find('website').set('text', info['site'])
		ui.find('website').set('url', info['site'])
		ui.find('desc').set('text', info['long'])

		if self._add is None:
			ui.remove('dlgAdd')

		if self._setup is not None:
			iface = self.waops.get_interface(self._setup)
			if iface.nomulti is True:
				for site in self.sites:
					if iface.name in site['type']:
						ui.remove('dlgSetup')
						self.put_message('err', 'Only one site of this type at any given time')
						return ui
			try:
				cfgui = self.app.inflate(iface.name.lower() + ':conf')
				ui.append('app-config', cfgui)
			except:
				ui.find('app-config').append(UI.Label(text="No config options available for this app"))
		else:
			ui.remove('dlgSetup')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			if self.apptypes == []:
				self.put_message('err', 'No webapp types installed. Check the Applications tab to find some')
			else:
				self._add = len(self.sites)
		if params[0] == 'drop':
			try:
				dt = self.sites[int(params[1])]
				self.waops.nginx_disable(dt['name'])
				self.waops.get_interface(dt['type']).remove(dt['name'])
			except Exception, e:
				self.put_message('err', 'Website removal failed: ' + str(e))
				self.app.log.error('Website removal failed: ' + str(e))
			else:
				self.put_message('info', 'Website successfully removed')
		if params[0] == 'enable':
			dt = self.sites[int(params[1])]
			self.waops.nginx_enable(dt['name'])
		if params[0] == 'disable':
			dt = self.sites[int(params[1])]
			self.waops.nginx_disable(dt['name'])

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				self._setup = self._current
			self._add = None
		if params[0] == 'dlgSetup':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '').lower()
				port = vars.getvalue('port', '80')
				if not name or not self._setup:
					self.put_message('err', 'Name or type not selected')
				elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
					self.put_message('err', 'Can\'t use the same port number as Genesis')
				else:
					cls = self.waops.get_interface(self._current)
					try:
						status = cls.install(name, vars)
					except Exception, e:
						self.put_message('err', 'Website add failed: ' 
							+ str(e))
						self.app.log.error('Website add failed: ' 
							+ str(e))
					else:
						if cls.php is True:
							self.waops.php_enable()
						try:
							self.waops.nginx_enable(name)
						except Exception, e:
							self.app.log.error(str(e))
							self.put_message('info',
								'App installed but services could not '
								'restart. Check the logs for info')
						else:
							self.put_message('info', 
								'%s added sucessfully' % name)
			self._setup = None

	@event('listitem/click')
	def on_list_click(self, event, params, vars=None):
		for p in self.apptypes:
			if p == params[0]:
				self._current = p
