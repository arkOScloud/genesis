from genesis.api import *
from genesis.ui import *
from genesis import apis

from utils import *


class DatabasesPlugin(apis.services.ServiceControlPlugin):
	text = 'Databases'
	iconfont = 'gen-database'
	folder = 'system'
	services = []

	def on_init(self):
		self.dbops = apis.databases(self.app)
		self.dbs = sorted(self.dbops.get_databases(), 
			key=lambda db: db['name'])
		self.users = sorted(self.dbops.get_users(), 
			key=lambda db: db['name'])
		self.dbtypes = sorted(self.dbops.get_dbtypes(), 
			key=lambda db: db[0])
		for dbtype in self.dbtypes:
			ok = True
			if dbtype[1] == '':
				ok = False
			for svc in self.services:
				if svc[1] == dbtype[1]:
					ok = False
			if ok == True:
				self.services.append((dbtype[0], dbtype[1]))

	def on_session_start(self):
		self._tab = 0
		self._add = None
		self._useradd = None
		self._chmod = None
		self._exec = None
		self._execmsg = ''
		self._import = None
		self._input = None
		self._output = None
		self._rootpwds = {}
		self._cancelauth = []

	def get_main_ui(self):
		ui = self.app.inflate('databases:main')
		ui.find('tabs').set('active', self._tab)
		t = ui.find('list')
		ut = ui.find('usrlist')
		st = ui.find('settings')
		tlbr = ui.find('toolbar')

		ubutton = False
		for dbtype in self.dbtypes:
			if dbtype[2] is False:
				self.put_message('err', 'The %s database process is not '
					'running. Your databases/users for this type will not '
					'appear until you start the process.' % dbtype[0])
				self.dbtypes.remove(dbtype)
			else:
				if self.dbops.get_interface(dbtype[0]).requires_conn == True and \
				not dbtype[0] in self._cancelauth and \
				not self.dbops.get_dbconn(dbtype[0]):
					ui.append('main', 
						UI.InputBox(id='dlgAuth%s' % dbtype[0], 
							text='Enter the database password for %s' 
							% dbtype[0],
							password=True)
					)
					self._rootpwds[dbtype[0]] = True
				elif self.dbops.get_interface(dbtype[0]).requires_conn == True and \
				not self.dbops.get_interface(dbtype[0]).checkpwstat():
					self._rootpwds[dbtype[0]] = False
					self.put_message('err', '%s does not have a root password set. '
						'Please add this via the Settings tab.' % dbtype[0])
					ubutton = True
				elif self.dbops.get_interface(dbtype[0]).multiuser == True:
					self._rootpwds[dbtype[0]] = True
					ubutton = True
				else:
					self._rootpwds[dbtype[0]] = True
			
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

		for dbtype in self.dbtypes:
			if self.dbops.get_interface(dbtype[0]).multiuser:
				st.append(UI.Label(text=dbtype[0], size='5'))
			if self.dbops.get_interface(dbtype[0]).multiuser and dbtype[0] in self._cancelauth:
				st.append(UI.Label(text='You must authenticate before changing these settings.'))
			elif self.dbops.get_interface(dbtype[0]).multiuser:
				st.append(UI.SimpleForm(
					UI.Formline(UI.EditPassword(id='newpasswd', value='Click to change'),
						text="New root password"
					),
					UI.Formline(UI.Button(onclick="form", form="frmPasswd%s" % dbtype[0],
						design="primary", action="OK", text="Change Password")),
					id="frmPasswd%s" % dbtype[0]
				))
			if self.dbops.get_interface(dbtype[0]).requires_conn:
				st.append(UI.Formline(UI.Button(text='Reauthenticate', id='reauth/'+dbtype[0])))

		if self._add is not None:
			type_sel = [UI.SelectOption(text = x[0], value = x[0])
                    for x in self.dbtypes]
			ui.appendAll('type', *type_sel)
		else:
			ui.remove('dlgAdd')

		if self._exec is not None:
			edlg = self.app.inflate('databases:execute')
			if self._execmsg:
				edlg.insertText('execmsg', self._execmsg)
				self._execmsg = ''
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
				cls = self.dbops.get_interface(dt['type'])
				if cls.requires_conn:
					cls.remove(dt['name'], self.app.session['dbconns'][dt['type']])
				else:
					cls.remove(dt['name'])
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
		if params[0] == 'reauth':
			if params[1] in self._cancelauth:
				self._cancelauth.remove(params[1])
			self.dbops.clear_dbconn(params[1])

	@event('form/submit')
	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				name = vars.getvalue('name', '')
				dbtype = vars.getvalue('type', '')
				if not name or not dbtype:
					self.put_message('err', 'Name or type not selected')
				elif self._rootpwds[dbtype] == False:
					self.put_message('err', 'Please add a root password for this database type via the Settings tab first.')
				else:
					cls = self.dbops.get_interface(dbtype)
					try:
						if cls.requires_conn:
							cls.add(name, self.app.session['dbconns'][dbtype])
						else:
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
		elif params[0] == 'dlgExec':
			if vars.getvalue('action', '') == 'OK':
				self._input = vars.getvalue('input', '')
				iface = self.dbops.get_interface(self._exec['type'])
				try:
					self._output = iface.execute(self._exec['name'], self._input)
				except Exception, e:
					self._execmsg = str(e[1])
			else:
				self._exec = None
		elif params[0] == 'dlgAddUser':
			if vars.getvalue('action', '') == 'OK':
				username = vars.getvalue('username')
				passwd = vars.getvalue('passwd')
				usertype = vars.getvalue('usertype', '')
				if not username or not usertype:
					self.put_message('err', 'Name or type not selected')
				elif self._rootpwds[usertype] == False:
					self.put_message('err', 'Please add a root password for this database type via the Settings tab first.')
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
		elif params[0] == 'dlgChmod':
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
		elif params[0].startswith('dlgAuth'):
			dbtype = params[0].split('dlgAuth')[1]
			if vars.getvalue('action', '') == 'OK':
				login = vars.getvalue('value', '')
				try:
					self.dbops.get_interface(dbtype).connect(
						store=self.app.session['dbconns'],
						passwd=login)
				except DBAuthFail, e:
					self.put_message('err', str(e))
			else:
				self.put_message('err', 'You refused to authenticate to %s. '
					'You will not be able to perform operations with this database type. '
					'Go to Settings and click Reauthenticate to retry.'% dbtype)
				self._cancelauth.append(dbtype)
		elif params[0].startswith('frmPasswd'):
			dbtype = params[0].split('frmPasswd')[1]
			v = vars.getvalue('newpasswd')
			if v != vars.getvalue('newpasswdb',''):
				self.put_message('err', 'Passwords must match')
			else:
				try:
					self.dbops.get_interface(dbtype).chpwstat(
						vars.getvalue('newpasswd'),
						self.app.session['dbconns'][dbtype]
						)
					self.put_message('info', 'Password for %s changed successfully' % dbtype)
				except Exception, e:
					self.put_message('err', 'Error changing password for %s: %s' % (dbtype, str(e)))
			self._tab = 2
