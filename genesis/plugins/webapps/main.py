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

		if self._add is not None:
			pass
		else:
			ui.remove('dlgAdd')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			if self.apptypes == []:
				self.put_message('err', 'No webapp types installed. Check the Applications tab to find some')
			else:
				self._add = len(self.sites)

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '')
				if not name or not self._current:
					self.put_message('err', 'Name or type not selected')
				else:
					cls = self.waops.get_interface(self._current)
					try:
						cls.install(name)
					except Exception, e:
						self.put_message('err', 'Website add failed: ' 
							+ str(e))
						self.app.log.error('Website add failed: ' 
							+ str(e))
					else:
						self.put_message('info', 
							'%s added sucessfully' % name)
			self._add = None

	@event('listitem/click')
	def on_list_click(self, event, params, vars=None):
		for p in self.apptypes:
			if p == params[0]:
				self._current = p
