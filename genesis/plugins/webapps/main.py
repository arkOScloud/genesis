from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import download

import backend


class WebAppsPlugin(CategoryPlugin):
	text = 'Websites'
	iconfont = 'gen-earth'
	folder = 'servers'

	def on_init(self):
		self.apiops = apis.webapps(self.app)
		self.mgr = backend.WABackend()
		self.sites = sorted(self.apiops.get_sites(), 
			key=lambda st: st['name'])
		self.apptypes = sorted(self.apiops.get_apptypes())
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
				(UI.OutLinkLabel(
					text=s['name'],
					url=s['addr']
					) if s['addr'] is not False else UI.Label(text=s['name'])),
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

		info = self.apiops.get_interface(self._current).get_info()
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
			iface = self.apiops.get_interface(self._setup)
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
				iface = self.apiops.get_interface(dt['type'])
				self.mgr.remove(dt['name'], iface)
			except Exception, e:
				self.put_message('err', 'Website removal failed: ' + str(e))
				self.app.log.error('Website removal failed: ' + str(e))
			else:
				self.put_message('info', 'Website successfully removed')
		if params[0] == 'enable':
			dt = self.sites[int(params[1])]
			self.mgr.nginx_enable(dt['name'])
		if params[0] == 'disable':
			dt = self.sites[int(params[1])]
			self.mgr.nginx_disable(dt['name'])

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
				samename = False
				for site in self.sites:
					if name == site['name']:
						samename = True
				if not name or not self._setup:
					self.put_message('err', 'Name or type not selected')
				elif samename is True:
					self.put_message('err', 'A site with this name already exists')
				elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
					self.put_message('err', 'Can\'t use the same port number as Genesis')
				else:
					try:
						iface = self.apiops.get_interface(self._current)
						self.mgr.add(name, iface, vars, True)
					except Exception, e:
						self.put_message('err', str(e))
						self.app.log.error(str(e))
					else:
						self.put_message('info', 
							'%s added sucessfully' % name)
			self._setup = None

	@event('listitem/click')
	def on_list_click(self, event, params, vars=None):
		for p in self.apptypes:
			if p == params[0]:
				self._current = p
