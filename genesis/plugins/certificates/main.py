from genesis.com import *
from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *
from genesis.plugins.network.backend import IHostnameManager

from backend import CertControl


class CertificatesPlugin(CategoryPlugin):
	text = 'Certificates'
	iconfont = 'gen-certificate'
	folder = 'system'

	def on_init(self):
		self.certs = sorted(self._cc.get_certs(),
			key=lambda x: x['name'])

	def on_session_start(self):
		self._cc = CertControl(self.app)
		self._gen = None
		self._wal = []
		self._pal = []

	def get_ui(self):
		ui = self.app.inflate('certificates:main')
		lst = ui.find('certlist')

		for s in self.certs:
			lst.append(UI.DTR(
				UI.IconFont(iconfont='gen-certificate'),
				UI.Label(text=s['name']),
				UI.Label(text=', '.join(filter(None, s['assign']))),
				UI.HContainer(
					UI.TipIcon(iconfont='gen-info', text='Information',
						id='info/' + str(self.certs.index(s))),
					UI.TipIcon(iconfont='gen-close', text='Delete',
						id='del/' + str(self.certs.index(s)),
						warning=('Are you sure you wish to remove this certificate? '
							'SSL on all associated services will be disabled'), ),
					),
			   ))

		if self._gen:
			self._wal, self._pal = self._cc.get_ssl_capable()
			alist, wlist, plist = [], [], []
			for cert in self.certs:
				for i in cert['assign']:
					if i != '':
						alist.append(i)
			if not 'Genesis SSL' in alist:
				ui.find('certassign').append(
					UI.Checkbox(text='Genesis SSL', name='genesis', value='genesis', checked=False),
				)
			for x in self._wal:
				if not (x['name']+' ('+x['type']+')') in alist:
					ui.find('certassign').append(
						UI.Checkbox(text=x['name'], name='wassign[]', value=x['name'], checked=False),
					)
					wlist.append(x)
			self._wal = wlist
			for x in self._pal:
				if not x.text in alist:
					ui.find('certassign').append(
						UI.Checkbox(text=x.text, name='passign[]', value=x.text, checked=False),
					)
					plist.append(x)
			self._pal = plist
		else:
			ui.remove('dlgGen')

		if self._cinfo:
			self._wal, self._pal = self._cc.get_ssl_capable()
			ui.find('certname').set('text', self._cinfo['name'])
			ui.find('domain').set('text', self._cinfo['domain'])
			exp = self._cinfo['expiry']
			exp = exp[0:4] + '-' + exp[4:6] + '-' + exp[6:8] + ', ' + exp[8:10] + ':' + exp[10:12]
			ui.find('expires').set('text', exp)

			alist = []
			for cert in self.certs:
				if cert != self._cinfo:
					for i in cert['assign']:
						if i != '':
							alist.append(i)

			if not 'Genesis SSL' in alist:
				if 'Genesis SSL' in self._cinfo['assign']:
					ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
				else:
					ic, ict, show = None, None, 'e'
				ui.find('certassign').append(
					UI.DTR(
						UI.IconFont(iconfont=ic, text=ict),
						UI.IconFont(iconfont='gen-arkos-round'),
						UI.Label(text='Genesis'),
						UI.HContainer(
							(UI.TipIcon(iconfont='gen-checkmark-circle',
								text='Assign', id='ac/'+self._cinfo['name']+'/g') if show == 'e' else None),
							(UI.TipIcon(iconfont='gen-close',
								text='Unassign', id='uc/'+self._cinfo['name']+'/g',
								warning=('Are you sure you wish to unassign this certificate? '
									'SSL on this service will be disabled, and you will need to '
									'reload Genesis for changes to take place.')) if show == 'd' else None),
						),
					)
				)
			for x in self._wal:
				if not (x['name']+' ('+x['type']+')') in alist:
					if (x['name']+' ('+x['type']+')') in self._cinfo['assign']:
						ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
					else:
						ic, ict, show = None, None, 'e'
					ui.find('certassign').append(
						UI.DTR(
							UI.IconFont(iconfont=ic, text=ict),
							UI.IconFont(iconfont='gen-earth'),
							UI.Label(text=x['name']),
							UI.HContainer(
								(UI.TipIcon(iconfont='gen-checkmark-circle',
									text='Assign', id='ac/'+self._cinfo['name']+'/w/'+str(self._wal.index(x))) if show == 'e' else None),
								(UI.TipIcon(iconfont='gen-close',
									text='Unassign', id='uc/'+self._cinfo['name']+'/w/'+str(self._wal.index(x)),
									warning=('Are you sure you wish to unassign this certificate? '
										'SSL on this service will be disabled.')) if show == 'd' else None),
							),
						)
					)
			for x in self._pal:
				if not x.text in alist:
					if x.text in self._cinfo['assign']:
						ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
					else:
						ic, ict, show = None, None, 'e'
					ui.find('certassign').append(
						UI.DTR(
							UI.IconFont(iconfont=ic, text=ict),
							UI.IconFont(iconfont=x.iconfont),
							UI.Label(text=x.text),
							UI.HContainer(
								(UI.TipIcon(iconfont='gen-checkmark-circle',
									text='Assign', id='ac/'+self._cinfo['name']+'/p/'+str(self._pal.index(x))) if show == 'e' else None),
								(UI.TipIcon(iconfont='gen-close',
									text='Unassign', id='uc/'+self._cinfo['name']+'/p/'+str(self._pal.index(x)),
									warning=('Are you sure you wish to unassign this certificate? '
										'SSL on this service will be disabled.')) if show == 'd' else None),
							),
						)
					)
		else:
			ui.remove('dlgInfo')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			pass
		elif params[0] == 'info':
			self._cinfo = self.certs[int(params[1])]
		elif params[0] == 'gen':
			self._gen = True
		elif params[0] == 'del':
			self._cc.remove(self.certs[int(params[1])]['name'])
			self.put_message('info', 'Certificate successfully deleted')
		elif params[0] == 'ac' and params[2] == 'p':
			self._cc.assign(self._cinfo['name'], 
				[('plugin', self._pal[int(params[3])])])
			self.put_message('info', '%s added to %s plugin' % (self._cinfo['name'], self._pal[int(params[3])].text))
			self._cinfo = None
		elif params[0] == 'ac' and params[2] == 'w':
			self._cc.assign(self._cinfo['name'],
				[('webapp', self._wal[int(params[3])])])
			self.put_message('info', '%s added to %s webapp' % (self._cinfo['name'], self._wal[int(params[3])]['name']))
			self._cinfo = None
		elif params[0] == 'ac' and params[2] == 'g':
			self._cc.assign(self._cinfo['name'], [[('genesis')]])
			self.put_message('info', '%s serving as Genesis certificate. Restart Genesis for changes to take effect' % self._cinfo['name'])
			self._cinfo = None
		elif params[0] == 'uc' and params[2] == 'p':
			self._cc.unassign(self._cinfo['name'], 
				[('plugin', self._pal[int(params[3])])])
			self.put_message('info', '%s removed from %s plugin, and SSL disabled.' % (self._cinfo['name'], self._pal[int(params[3])].text))
			self._cinfo = None
		elif params[0] == 'uc' and params[2] == 'w':
			self._cc.unassign(self._cinfo['name'],
				[('webapp', self._wal[int(params[3])])])
			self.put_message('info', '%s removed from %s webapp, and SSL disabled.' % (self._cinfo['name'], self._wal[int(params[3])]['name']))
			self._cinfo = None
		elif params[0] == 'uc' and params[2] == 'g':
			self._cc.unassign(self._cinfo['name'], [[('genesis')]])
			self.put_message('info', 'Certificate removed and SSL disabled for Genesis. Restart Genesis for changes to take effect')
			self._cinfo = None

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				pass
		elif params[0] == 'dlgGen':
			if vars.getvalue('action', '') == 'OK':
				if vars.getvalue('certname', '') == '':
					self.put_message('err', 'Certificate name is mandatory')
				elif vars.getvalue('certname', '') in [x['name'] for x in self.certs]:
					self.put_message('err', 'You already have a certificate with that name.')
				else:
					lst = []
					if vars.getvalue('genesis', '') == '1':
						lst.append([('genesis')])
					for i in range(0, len(self._wal)):
						try:
							if vars.getvalue('wassign[]')[i] == '1':
								lst.append(('webapp', self._wal[i]))
						except TypeError:
							pass
					for i in range(0, len(self._pal)):
						try:
							if vars.getvalue('passign[]')[i] == '1':
								lst.append(('plugin', self._pal[i]))
						except TypeError:
							pass
					cgw = CertGenWorker(self, vars.getvalue('certname'), vars, lst)
					cgw.start()
			self._wal = []
			self._pal = []
			self._gen = False
		elif params[0] == 'dlgInfo':
			self._cinfo = None
			self._wal = []
			self._pal = []


class CertGenWorker(BackgroundWorker):
	def __init__(self, *args):
		BackgroundWorker.__init__(self, *args)

	def run(self, cat, name, vars, assign):
		cat.put_statusmsg('Generating a certificate and key...')
		try:
			CertControl(cat.app).gencert(name, vars, 
				cat.app.get_backend(IHostnameManager).gethostname())
		except Exception, e:
			cat.clr_statusmsg()
			cat.put_message('err', str(e))
			cat.app.log.error(str(e))
		cat.put_statusmsg('Assigning new certificate...')
		CertControl(cat.app).assign(name, assign)
		cat.clr_statusmsg()
		cat.put_message('info', 'Certificate successfully generated')
