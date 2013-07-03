from genesis.api import *
from genesis.ui import *
from genesis import apis

from backend import *


class DatabasesPlugin(CategoryPlugin):
	text = 'Databases'
	iconfont = 'gen-database'
	folder = 'system'

	def on_init(self):
		self.dbops = DBOps(self.app)
		getdbs = self.dbops.get_databases()
		self.dbs = []
		for lt in getdbs:
			for item in lt:
				self.dbs.append(item)

	def on_session_start(self):
	    self._add = None
	    self._exec = None

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
						iconfont='gen-target',
						id='exec/' + str(self.dbs.index(d)),
						text='Execute'
					),
					UI.TipIcon(
						iconfont='gen-cancel-circle',
						id='drop/' + str(self.dbs.index(d)),
						text='Delete',
						warning='Delete database %s'%d['name']
						)
					),
				))

		if self._add is not None:
			type_sel = [UI.SelectOption(text = x, value = x)
                    for x in self.dbops.get_dbtypes()]
			ui.appendAll('type', *type_sel)
		else:
			ui.remove('dlgAdd')

		if self._exec is not None:
			# TODO
			pass
		else:
			ui.remove('dlgExec')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			self._add = len(self.dbs)
		if params[0] == 'exec':
			cmds = ''
			dt = self.dbs[int(params[1])]
			out = self.dbops.get_dbcls(dt['type']).execute(dt['name'], cmds)
		if params[0] == 'drop':
			try:
				dt = self.dbs[int(params[1])]
				self.dbops.get_dbcls(dt['type']).remove(dt['name'])
			except Exception, e:
				self.put_message('err', 'Database drop failed: ' + str(e))
				self.app.log.error('Database drop failed: ' + str(e))
			else:
				self.dbs.pop(int(params[1]))
				self.put_message('info', 'Database successfully dropped')

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '')
				dbtype = vars.getvalue('type', '')
				if not name or not dbtype:
					self.put_message('err', 'Name or type not selected')
				else:
					cls = self.dbops.get_dbcls(dbtype)
					try:
						cls.add(name)
					except Exception, e:
						self.put_message('err', 'Database add failed: ' + str(e))
						self.app.log.error('Database add failed: ' + str(e))
					else:
						self.put_message('info', 'Database %s added sucessfully' % name)
			self._add = None
		if params[0] == 'frmExec':
			# TODO
			pass
		if params[0] == 'dlgExec':
			self._exec = None
