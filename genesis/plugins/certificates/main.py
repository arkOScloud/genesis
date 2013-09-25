from genesis.com import *
from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *


class CertificatesPlugin(CategoryPlugin):
	text = 'Certificates'
	iconfont = 'gen-certificate'
	folder = 'system'

	def on_init(self):
		pass

	def on_session_start(self):
		pass

	def get_ui(self):
		ui = self.app.inflate('certificates:main')
		return ui

	@event('button/click')
	def on_click(self, event, params, vars = None):
		if params[0] == 'add':
			pass

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		if params[0] == 'dlgAdd':
			if vars.getvalue('action', '') == 'OK':
				pass


class CertGenWorker(BackgroundWorker):
	def __init__(self, *args):
		BackgroundWorker.__init__(self, *args)

	def run(self):
		pass
