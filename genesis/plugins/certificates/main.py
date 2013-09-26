from genesis.com import *
from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *

from backend import CertControl


class CertificatesPlugin(CategoryPlugin):
	text = 'Certificates'
	iconfont = 'gen-certificate'
	folder = 'system'

	def on_init(self):
		self.certs = sorted(self._cc.get_certs(),
			lambda x: x['name'])

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
				UI.Label(text=', '.join(s['assign'])),
				UI.HContainer(
					UI.TipIcon(iconfont='gen-info', text='Information',
						id='info/' + str(self.certs.index(s))),
					UI.TipIcon(iconfont='gen-close', text='Delete',
						id='del/' + str(self.certs.index(s))),
					),
			   ))

		if self._gen:
			self._wal, self._pal = self._cc.get_ssl_capable()
			for x in self._wal:
				ui.find('certassign').append(
					UI.Checkbox(text=x['name'], name='wassign[]', value=x['name'], checked=False),
				)
			for x in self._pal:
				ui.find('certassign').append(
					UI.Checkbox(text=x.text, name='passign[]', value=x.text, checked=False),
				)
		else:
			ui.remove('dlgGen')

		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			pass
		if params[0] == 'gen':
			self._gen = True
		if params[0] == 'del':
			self._cc.remove(self.certs[int(params[1])]['name'])
			for a in self.certs[int(params[1])]['assign']:
				pass

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				pass
		if params[0] == 'dlgGen':
			if vars.getvalue('action', '') == 'OK':
				lst = []
				for i in range(0, len(self._wal)):
					if vars.getvalue('wassign[]')[i] == '1':
						lst.append(('webapp', self._wal[i]))
				for i in range(0, len(self._pal)):
					if vars.getvalue('passign[]')[i] == '1':
						lst.append(('plugin', self._pal[i]))
				cgw = CertGenWorker(self, vars.getvalue('certname'), lst)
				cgw.start()
			self._gen = False


class CertGenWorker(BackgroundWorker):
	def __init__(self, *args):
		BackgroundWorker.__init__(self, *args)

	def run(self, cat, name, assign):
		cat.put_statusmsg('Generating a certificate and key...')
		CertControl(cat.app).gencert(name)
		cat.put_statusmsg('Assigning new certificate...')
		CertControl(cat.app).assign(name, assign)
		cat.clr_statusmsg()
