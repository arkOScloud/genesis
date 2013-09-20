from genesis.com import *
from genesis.api import *
from genesis.plugins.core.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *

from backend import WABackend


class WebAppsPlugin(apis.services.ServiceControlPlugin):
	text = 'Websites'
	iconfont = 'gen-earth'
	folder = 'servers'
	services = []

	def on_init(self):
		if self._relsec != None:
			if self._relsec[0] == 'add':
				apis.networkcontrol(self.app).add_webapp(self._relsec[1])
				self._relsec = None
			elif self._relsec[0] == 'del':
				apis.networkcontrol(self.app).remove_webapp(self._relsec[1])
			self._relsec = None
		self.services = []
		self.apiops = apis.webapps(self.app)
		self.mgr = WABackend()
		self.sites = sorted(self.apiops.get_sites(), 
			key=lambda st: st['name'])
		ats = sorted(self.apiops.get_apptypes(), key=lambda x: x.name.lower())
		self.apptypes = sorted(ats, key=lambda x: (hasattr(x, 'sort')))
		if len(self.sites) != 0:
			self.services.append(('Web Server', 'nginx'))
		if not self._current:
			self._current = self.apptypes[0]
		for apptype in self.apptypes:
			ok = False
			for site in self.sites:
				if site['type'] == apptype.name:
					ok = True
			if ok == False:
				continue
			if hasattr(apptype, 'services'):
				for dep in apptype.services:
					post = True
					for svc in self.services:
						if svc[1] == dep[1]:
							post = False
					if post == True:
						self.services.append((dep[0], dep[1]))

	def on_session_start(self):
		self._add = None
		self._edit = None
		self._setup = None
		self._relsec = None

	def get_main_ui(self):
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
						warning='Are you sure you wish to delete site %s? This action is irreversible.'%s['name']
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
						ui.remove('dlgEdit')
						self.put_message('err', 'Only one site of this type at any given time')
						self._setup = None
						return ui
			try:
				if self._setup.name == 'Website':
					cfgui = self.app.inflate('webapps:conf')
					type_sel = [UI.SelectOption(text='None', value='None')]
					for x in sorted(apis.databases(self.app).get_dbtypes()):
						type_sel.append(UI.SelectOption(text=x[0], value=x[0]))
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
			w = WAWorker(self, 'drop', self.sites[int(params[1])])
			w.start()
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
				elif vars.getvalue('cfgport') == self.app.gconfig.get('genesis', 'bind_port', ''):
					self.put_message('err', 'Can\'t use the same port number as Genesis')
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
				apis.networkcontrol(self.app).change_webapp(
					self._edit['name'], vars.getvalue('cfgname'), 
					self._edit['type'], vars.getvalue('cfgport'))
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
					w = WAWorker(self, 'add', name, self._current, vars)
					w.start()
					
			self._setup = None

	@event('listitem/click')
	def on_list_click(self, event, params, vars=None):
		for p in self.apptypes:
			if p.name == params[0]:
				self._current = p


class WAWorker(BackgroundWorker):
	def __init__(self, *args):
		self.backend = WABackend()
		BackgroundWorker.__init__(self, *args)

	def run(self, cat, action, name, current='', vars=None):
		if action == 'add':
			try:
				spmsg = self.backend.add(cat, name, current, vars, True)
			except Exception, e:
				cat.clr_statusmsg()
				cat.put_message('err', str(e))
				cat.app.log.error(str(e))
			else:
				cat.put_message('info', 
					'%s added sucessfully' % name)
				cat._relsec = ('add', (name, current, vars))
				if spmsg:
					cat.put_message('info', spmsg)
		elif action == 'drop':
			try:
				self.backend.remove(cat, name)
			except Exception, e:
				cat.clr_statusmsg()
				cat.put_message('err', 'Website removal failed: ' + str(e))
				cat.app.log.error('Website removal failed: ' + str(e))
			else:
				cat.put_message('info', 'Website successfully removed')
				cat._relsec = ('del', name['name'])
