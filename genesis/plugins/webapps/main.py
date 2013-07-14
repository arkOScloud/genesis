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
		ats = sorted(self.apiops.get_apptypes(), key=lambda x: x.name.lower())
		self.apptypes = sorted(ats, key=lambda x: (hasattr(x, 'sort')))
		if not self._current:
			self._current = self.apptypes[0]

	def on_session_start(self):
		self._add = None
		self._edit = None
		self._setup = None

	def get_ui(self):
		ui = self.app.inflate('webapps:main')
		t = ui.find('list')

		for s in self.sites:
			if s['addr'] is not False:
				addr = 'http://' + s['addr'] + (':'+s['port'] if s['port'] is not '80' else '')
			else:
				addr = False

			t.append(UI.DTR(
				UI.Iconfont(iconfont="gen-earth"),
				(UI.OutLinkLabel(
					text=s['name'],
					url=addr
					) if s['addr'] is not False else UI.Label(text=s['name'])
				),
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
						UI.Label(text=apptype.name),
						id=apptype.name,
						active=apptype.name==self._current.name
					)
				)

		info = self._current.get_info()
		if info['logo'] is True:
			ui.find('logo').set('file', '/dl/'+info['name'].lower()+'/logo.png')
		ui.find('appname').set('text', info['name'])
		ui.find('short').set('text', info['short'])
		if info['site'] is None:
			ui.find('website').set('text', 'None')
			ui.find('website').set('url', 'http://localhost')
		else:
			ui.find('website').set('text', info['site'])
			ui.find('website').set('url', info['site'])
		ui.find('desc').set('text', info['long'])

		if self._add is None:
			ui.remove('dlgAdd')

		if self._setup is not None:
			if self._setup.nomulti is True:
				for site in self.sites:
					if self._setup.name in site['type']:
						ui.remove('dlgSetup')
						self.put_message('err', 'Only one site of this type at any given time')
						self._setup = None
						return ui
			try:
				if self._setup.name == 'Website':
					cfgui = self.app.inflate('webapps:conf')
					type_sel = [UI.SelectOption(text='None', value='None')]
					for x in sorted(apis.databases(self.app).get_dbtypes()):
						type_sel.append(UI.SelectOption(text = x, value = x))
					cfgui.appendAll('ws-dbsel', *type_sel)
				else:
					cfgui = self.app.inflate(self._setup.name.lower() + ':conf')
				ui.append('app-config', cfgui)
			except:
				raise
				ui.find('app-config').append(UI.Label(text="No config options available for this app"))
		else:
			ui.remove('dlgSetup')

		if self._edit is not None:
			ui.find('cfgname').set('value', self._edit['name'])
			ui.find('cfgaddr').set('value', self._edit['addr'])
			ui.find('cfgport').set('value', self._edit['port'])
		else:
			ui.remove('dlgEdit')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			if self.apptypes == []:
				self.put_message('err', 'No webapp types installed. Check the Applications tab to find some')
			else:
				self._add = len(self.sites)
		if params[0] == 'config':
			self._edit = self.sites[int(params[1])]
		if params[0] == 'drop':
			try:
				self.mgr.remove(self.sites[int(params[1])])
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
		if params[0] == 'dlgEdit':
			if vars.getvalue('action', '') == 'OK':
				if vars.getvalue('cfgname', '') == '':
					self.put_message('err', 'Must choose a name')
				elif vars.getvalue('cfgaddr', '') == '':
					self.put_message('err', 'Must choose an address')
				elif vars.getvalue('cfgport', '') == '':
					self.put_message('err', 'Must choose a port (default 80)')
				else:
					self.mgr.nginx_edit(
						origname=self._edit['name'], 
						name=vars.getvalue('cfgname'), 
						stype=self._edit['type'], 
						path=self._edit['path'], 
						addr=vars.getvalue('cfgaddr'), 
						port=vars.getvalue('cfgport'), 
						php=self._edit['php']
						)
			self._edit = None
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
						self.mgr.add(name, self._current, vars, True)
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
			if p.name == params[0]:
				self._current = p
