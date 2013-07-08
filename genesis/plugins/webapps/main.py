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

		if self._add is not None:
			type_sel = [UI.SelectOption(text = x, value = x)
				for x in self.apptypes]
			ui.appendAll('type', *type_sel)
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
				apptype = vars.getvalue('type', '')
				if not name or not apptype:
					self.put_message('err', 'Name or type not selected')
				else:
					cls = self.waops.get_interface(apptype)
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
