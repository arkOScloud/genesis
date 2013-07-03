from genesis.api import *
from genesis.ui import *
from genesis import apis


class DatabasesPlugin(CategoryPlugin):
	text = 'Databases'
	iconfont = 'gen-database'
	folder = 'system'

	def on_init(self):
		self.dbops = apis.dbops(self.app)
		self.dbs = sorted(self.dbops.get_databases(), key=lambda db: db['name'])

	def on_session_start(self):
	    self._add = None
	    self._exec = None
	    self._input = None
	    self._output = None

	def get_ui(self):
		ui = self.app.inflate('databases:main')
		t = ui.find('list')

		for d in self.dbs:
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
			edlg = self.app.inflate('databases:execute')
			if self._input is not None:
				elem = edlg.find('input')
				elem.set('value', self._input)
			if self._output is not None:
				elem = edlg.find('output')
				elem.set('value', self._output)
			ui.append('main', edlg)
		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			self._add = len(self.dbs)
		if params[0] == 'exec':
			self._exec = self.dbs[int(params[1])]
			self._input = None
			self._output = None
		if params[0] == 'drop':
			try:
				dt = self.dbs[int(params[1])]
				self.dbops.get_dbcls(dt['type']).remove(dt['name'])
			except Exception, e:
				self.put_message('err', 'Database drop failed: ' + str(e))
				self.app.log.error('Database drop failed: ' + str(e))
			else:
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
		if params[0] == 'dlgExec':
			if vars.getvalue('action', '') == 'OK':
				self._input = vars.getvalue('input', '')
				self._output = self.dbops.get_dbcls(self._exec['type']).execute(self._exec['name'], self._input)
			else:
				self._exec = None
