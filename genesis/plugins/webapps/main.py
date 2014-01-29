from genesis.com import *
from genesis.api import *
from genesis.plugins.core.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *
from genesis.plugins.databases.utils import *

import re

from backend import WebappControl
from api import Webapp


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
		self.dbops = apis.databases(self.app)
		self.mgr = WebappControl(self.app)
		self.sites = sorted(self.apiops.get_sites(), 
			key=lambda st: st.name)
		ats = sorted(self.apiops.get_apptypes(), key=lambda x: x.name.lower())
		self.apptypes = sorted(ats, key=lambda x: (hasattr(x, 'sort')))
		if len(self.sites) != 0:
			self.services.append(('Web Server', 'nginx'))
		if not self._current:
			self._current = self.apptypes[0]
		for apptype in self.apptypes:
			ok = False
			for site in self.sites:
				if site.stype == apptype.name:
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
		self._dbauth = ('','','')

	def get_main_ui(self):
		ui = self.app.inflate('webapps:main')
		t = ui.find('list')

		for s in self.sites:
			if s.addr and s.ssl:
				addr = 'https://' + s.addr + (':'+s.port if s.port != '443' else '')
			elif s.addr:
				addr = 'http://' + s.addr + (':'+s.port if s.port != '80' else '')
			else:
				addr = False

			t.append(UI.DTR(
				UI.Iconfont(iconfont="gen-earth"),
				(UI.OutLinkLabel(
					text=s.name,
					url=addr
					) if s.addr is not False else UI.Label(text=s.name)
				),
				UI.Label(text=s.stype),
				UI.HContainer(
					UI.TipIcon(
						iconfont='gen-minus-circle' if s.enabled else 'gen-checkmark-circle',
						id=('disable/' if s.enabled else 'enable/') + str(self.sites.index(s)),
						text='Disable' if s.enabled else 'Enable'
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
						warning='Are you sure you wish to delete site %s? This action is irreversible.'%s.name
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
			ui.find('logo').set('file', '/dl/'+self._current.__class__.__name__.lower()+'/logo.png')
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
					if self._setup.name in site.stype:
						ui.remove('dlgSetup')
						ui.remove('dlgEdit')
						self.put_message('err', 'Only one site of this type at any given time')
						self._setup = None
						return ui
			try:
				if self._setup.name == 'Website':
					cfgui = self.app.inflate('webapps:conf')
					type_sel = [UI.SelectOption(text='None', value='None')]
					for x in sorted(self.dbops.get_dbtypes()):
						type_sel.append(UI.SelectOption(text=x[0], value=x[0]))
					cfgui.appendAll('ws-dbsel', *type_sel)
				else:
					cfgui = self.app.inflate(self._setup.__class__.__name__.lower() + ':conf')
				ui.append('app-config', cfgui)
			except:
				ui.find('app-config').append(UI.Label(text="No config options available for this app"))
		else:
			ui.remove('dlgSetup')

		if self._edit is not None:
			try:
				edgui = self.app.inflate(self._edit.stype.lower() + ':edit')
				ui.append('dlgEdit', edgui)
			except:
				pass
			ui.find('cfgname').set('value', self._edit.name)
			ui.find('cfgaddr').set('value', self._edit.addr)
			ui.find('cfgport').set('value', self._edit.port)
		else:
			ui.remove('dlgEdit')

		if self._dbauth[0] and not self.dbops.get_interface(self._dbauth[0]).checkpwstat():
			self.put_message('err', '%s does not have a root password set. '
				'Please add this via the Databases screen.' % self._dbauth[0])
			self._dbauth = ('','','')
		if self._dbauth[0]:
			ui.append('main', UI.InputBox(id='dlgAuth%s' % self._dbauth[0], 
				text='Enter the database password for %s' 
				% self._dbauth[0], password=True))

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			if self.apptypes == []:
				self.put_message('err', 'No webapp types installed. Check the Applications tab to find some')
			else:
				self._add = len(self.sites)
		elif params[0] == 'config':
			self._edit = self.sites[int(params[1])]
		elif params[0] == 'drop':
			if hasattr(self.sites[int(params[1])].sclass, 'dbengine') and \
			self.dbops.get_interface(self.sites[int(params[1])].sclass.dbengine).requires_conn and \
			not self.dbops.get_dbconn(self.sites[int(params[1])].sclass.dbengine):
				self._dbauth = (self.sites[int(params[1])].sclass.dbengine, 
					self.sites[int(params[1])], 'drop')
			else:
				w = WAWorker(self, 'drop', self.sites[int(params[1])])
				w.start()
		elif params[0] == 'enable':
			self.mgr.nginx_enable(self.sites[int(params[1])])
		elif params[0] == 'disable':
			self.mgr.nginx_disable(self.sites[int(params[1])])
		else: 
			for x in self.apptypes:
				if x.name.lower() == params[0]:
					speccall = getattr(x, params[1])
					speccall(self._edit)

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				if hasattr(self._current, 'dbengine'):
					on = False
					for dbtype in self.dbops.get_dbtypes():
						if self._current.dbengine == dbtype[0] and dbtype[2] == True:
							on = True
						elif self._current.dbengine == dbtype[0] and dbtype[2] == None:
							on = True
					if on:
						if self.dbops.get_interface(self._current.dbengine).requires_conn and \
						not self.dbops.get_dbconn(self._current.dbengine):
							self._dbauth = (self._current.dbengine, '', 'add')
						else:
							self._setup = self._current
					else:
						self.put_message('err', 'The database engine for %s is not running. Please start it via the Status button.' % self._current.dbengine)
				else:
					self._setup = self._current
			self._add = None
		if params[0] == 'dlgEdit':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('cfgname', '')
				if name == '':
					self.put_message('err', 'Must choose a name')
				elif re.search('\.|-|`|\\\\|\/|^test$|[ ]', name):
					self.put_message('err', 'Site name must not contain spaces, dots, dashes or special characters')
				elif vars.getvalue('cfgaddr', '') == '':
					self.put_message('err', 'Must choose an address')
				elif vars.getvalue('cfgport', '') == '':
					self.put_message('err', 'Must choose a port (default 80)')
				elif vars.getvalue('cfgport') == self.app.gconfig.get('genesis', 'bind_port', ''):
					self.put_message('err', 'Can\'t use the same port number as Genesis')
				else:
					w = Webapp()
					w.name = vars.getvalue('cfgname')
					w.stype = self._edit.stype
					w.path = self._edit.path
					w.addr = vars.getvalue('cfgaddr') 
					w.port = vars.getvalue('cfgport')
					w.ssl = self._edit.ssl
					w.php = self._edit.php
					self.mgr.nginx_edit(self._edit, w)
					apis.networkcontrol(self.app).change_webapp(self._edit, w)
			self._edit = None
		if params[0] == 'dlgSetup':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '').lower()
				port = vars.getvalue('port', '80')
				samename = False
				for site in self.sites:
					if name == site.name:
						samename = True
				if not name or not self._setup:
					self.put_message('err', 'Name or type not selected')
				elif samename is True:
					self.put_message('err', 'A site with this name already exists')
				elif port == self.app.gconfig.get('genesis', 'bind_port', ''):
					self.put_message('err', 'Can\'t use the same port number as Genesis')
				elif re.search('\.|-|`|\\\\|\/|^test$|[ ]', name):
					self.put_message('err', 'Site name must not contain spaces, dots, dashes or special characters')
				else:
					w = WAWorker(self, 'add', name, self._current, vars)
					w.start()
			self._setup = None
		if params[0].startswith('dlgAuth'):
			dbtype = params[0].split('dlgAuth')[1]
			if vars.getvalue('action', '') == 'OK':
				login = vars.getvalue('value', '')
				try:
					dbauth = self._dbauth
					self._dbauth = ('','','')
					self.dbops.get_interface(dbtype).connect(
						store=self.app.session['dbconns'],
						passwd=login)
					if dbauth[2] == 'drop':
						w = WAWorker(self, 'drop', dbauth[1])
						w.start()
					elif dbauth[2] == 'add':
						self._setup = self._current
				except DBAuthFail, e:
					self.put_message('err', str(e))
			else:
				self.put_message('info', 'Website %s cancelled' % self._dbauth[2])
				self._dbauth = ('','','')

	@event('listitem/click')
	def on_list_click(self, event, params, vars=None):
		for p in self.apptypes:
			if p.name == params[0]:
				self._current = p


class WAWorker(BackgroundWorker):
	def run(self, cat, action, site, current='', vars=None):
		if action == 'add':
			try:
				spmsg = WebappControl(cat.app).add(
					cat, site, current, vars, True)
			except Exception, e:
				cat.clr_statusmsg()
				cat.put_message('err', str(e))
				cat.app.log.error(str(e))
			else:
				cat.put_message('info', 
					'%s added sucessfully' % site)
				cat._relsec = ('add', (site, current, vars))
				if spmsg:
					cat.put_message('info', spmsg)
		elif action == 'drop':
			try:
				WebappControl(cat.app).remove(cat, site)
			except Exception, e:
				cat.clr_statusmsg()
				cat.put_message('err', 'Website removal failed: ' + str(e))
				cat.app.log.error('Website removal failed: ' + str(e))
			else:
				cat.put_message('info', 'Website successfully removed')
				cat._relsec = ('del', site.name)
