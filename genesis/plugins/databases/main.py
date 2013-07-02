from genesis.api import *
from genesis.ui import *
from genesis import apis

from backend import *


class DatabasesPlugin(CategoryPlugin):
	text = 'Databases'
	iconfont = 'gen-database'
	folder = 'system'

	def on_init(self):
		self._add = ''
		self.dbops = DBOps(self.app)
		getdbs = self.dbops.get_databases()
		self.dbs = []
		for lt in getdbs:
			for item in lt:
				self.dbs.append(item)

	def get_ui(self):
		ui = self.app.inflate('databases:main')
		t = ui.find('list')

		for d in sorted(self.dbs, key=lambda db: db['name']):
			t.append(UI.DTR(
				UI.Iconfont(iconfont="gen-database"),
				UI.Label(text=d['name']),
				UI.Label(text=d['type']),
				UI.HContainer(
					UI.TipIcon(
						iconfont='gen-cancel-circle',
						id='drop/' + str(self.dbs.index(d)),
						text='Delete',
						warning='Delete database %s'%d['name']
						)
					),
				))
		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			self._add = len(self.dbs)
		if params[0] == 'drop':
			try:
				dt = self.dbs[int(params[1])]
				self.dbops.get_dbcls(dt['type']).remove(dt['name'])
			except Exception, e:
				self.put_message('err', 'Database couldn\t be dropped')
				self.app.log.error('Database drop failed: ' + str(e))
			else:
				self.dbs.pop(int(params[1]))
				self.put_message('info', 'Database successfully dropped')

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			self._editing = None
