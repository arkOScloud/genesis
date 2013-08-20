from genesis.api import *
from genesis.ui import *
from genesis import apis


class DatabasesPlugin(CategoryPlugin):
	text = 'Databases'
	iconfont = 'gen-database'
	folder = 'system'

	def on_init(self):
		self.dbops = apis.databases(self.app)
		self.dbs = sorted(self.dbops.get_databases(), 
			key=lambda db: db['name'])
		self.users = sorted(self.dbops.get_users(), 
			key=lambda db: db['name'])
		self.dbtypes = sorted(self.dbops.get_dbtypes(), 
			key=lambda db: db[0])

	def on_session_start(self):
		self._tab = 0
		self._add = None
		self._useradd = None
		self._chmod = None
		self._exec = None
		self._import = None
		self._input = None
		self._output = None

	def get_ui(self):
		ui = self.app.inflate('databases:main')
		ui.find('tabs').set('active', self._tab)
		t = ui.find('list')
		ut = ui.find('usrlist')
		tlbr = ui.find('toolbar')

		for dbtype in self.dbtypes:
			if dbtype[1] is False:
				self.put_message('err', 'The %s database process is not '
					'running. Your databases/users for this type will not '
					'appear until you start the process.' % dbtype[0])

		ubutton = False
		for dbtype in self.dbtypes:
			if self.dbops.get_interface(dbtype[0]).multiuser == True:
				ubutton = True
		if ubutton == True:
			tlbr.append(
				UI.Button(
					id="adduser",
					text="Add user",
					iconfont="gen-user-plus"
					)
				)

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
						warning='Are you sure you wish to delete database %s? This may prevent any applications using it from functioning properly.'%d['name']
						)
					),
				))

		for u in self.users:
			ut.append(UI.DTR(
				UI.Iconfont(iconfont="gen-user"),
				UI.Label(text=u['name']),
				UI.Label(text=u['type']),
				UI.HContainer(
					UI.TipIcon(
						iconfont='gen-tools',
						id='chmod/' + str(self.users.index(u)),
						text='Grant/Revoke Permissions'
					),
					UI.TipIcon(
						iconfont='gen-cancel-circle',
						id='deluser/' + str(self.users.index(u)),
						text='Delete',
						warning='Are you sure you wish to delete user %s? This may prevent any applications using it from functioning properly.'%u['name']
						)
					),
				))

		if self._add is not None:
			type_sel = [UI.SelectOption(text = x[0], value = x[0])
                    for x in self.dbtypes]
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

		if self._useradd is not None:
			type_sel = []
			for x in self.dbtypes:
				if self.dbops.get_interface(x[0]).multiuser == True:
					type_sel.append(UI.SelectOption(text=x[0], value=x[0]))
			ui.appendAll('usertype', *type_sel)
		else:
			ui.remove('dlgAddUser')

		if self._chmod is not None:
			iface = self.dbops.get_interface(self._chmod['type'])
			plist = iface.chperm('', self._chmod['name'], 'check')
			dblist = [UI.SelectOption(text=x['name'], value=x['name'])
					for x in iface.get_dbs()]
			ui.find('permlist').set('value', plist)
			ui.appendAll('dblist', *dblist)
		else:
			ui.remove('dlgChmod')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			if self.dbtypes == []:
				self.put_message('err', 'No database engines installed. Check the Applications tab to find some')
			else:
				self._add = len(self.dbs)
			self._tab = 0
		if params[0] == 'adduser':
			self._useradd = len(self.users)
			self._tab = 1
		if params[0] == 'exec':
			self._exec = self.dbs[int(params[1])]
			self._input = None
			self._output = None
			self._tab = 0
		if params[0] == 'chmod':
			self._chmod = self.users[int(params[1])]
			self._tab = 1
		if params[0] == 'import':
			self._import = True
			self._tab = 0
		if params[0] == 'drop':
			self._tab = 0
			try:
				dt = self.dbs[int(params[1])]
				self.dbops.get_interface(dt['type']).remove(dt['name'])
			except Exception, e:
				self.put_message('err', 'Database drop failed: ' + str(e))
				self.app.log.error('Database drop failed: ' + str(e))
			else:
				self.put_message('info', 'Database successfully dropped')
		if params[0] == 'deluser':
			self._tab = 1
			try:
				dt = self.users[int(params[1])]
				iface = self.dbops.get_interface(dt['type'])
				iface.usermod(dt['name'], 'del', '')
			except Exception, e:
				self.put_message('err', 'User drop failed: ' + str(e))
				self.app.log.error('User drop failed: ' + str(e))
			else:
				self.put_message('info', 'User deleted') 

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '')
				dbtype = vars.getvalue('type', '')
				if not name or not dbtype:
					self.put_message('err', 'Name or type not selected')
				else:
					cls = self.dbops.get_interface(dbtype)
					try:
						cls.add(name)
					except Exception, e:
						self.put_message('err', 'Database add failed: ' 
							+ str(e))
						self.app.log.error('Database add failed: ' 
							+ str(e))
					else:
						self.put_message('info', 
							'Database %s added sucessfully' % name)
			self._add = None
		if params[0] == 'dlgExec':
			if vars.getvalue('action', '') == 'OK':
				self._input = vars.getvalue('input', '')
				iface = self.dbops.get_interface(self._exec['type'])
				self._output = iface.execute(self._exec['name'], self._input)
			else:
				self._exec = None
		if params[0] == 'dlgAddUser':
			if vars.getvalue('action', '') == 'OK':
				username = vars.getvalue('username')
				passwd = vars.getvalue('passwd')
				usertype = vars.getvalue('usertype', '')
				if not username or not usertype:
					self.put_message('err', 'Name or type not selected')
				else:
					try:
						iface = self.dbops.get_interface(usertype)
						iface.usermod(username, 'add', passwd)
					except Exception, e:
						self.put_message('err', 'User add failed: '
							+ str(e))
						self.app.log.error('User add failed: '
							+ str(e))
					else:
						self.put_message('info',
							'User %s added successfully' % username)
			self._useradd = None
		if params[0] == 'dlgChmod':
			if vars.getvalue('action', '') == 'OK':
				action = vars.getvalue('chperm', '')
				dbname = vars.getvalue('dblist', '')
				try:
					iface = self.dbops.get_interface(self._chmod['type'])
					iface.chperm(dbname, self._chmod['name'], action)
				except Exception, e:
					self.put_message('err', 'Permission change failed, see logs')
					self.app.log.error('Permission change failed: '
						+ str(e))
				else:
					self.put_message('info',
						'Permissions for %s changed successfully' % self._chmod['name'])
			self._chmod = None
