from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs, download

import os
import ast


class ownCloud(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'ownCloud'
	dpath = 'http://download.owncloud.org/community/owncloud-5.0.7.tar.bz2'
	icon = 'gen-cloud'

	def install(self, name):
		pass

	def remove(self, name):
		pass

	def get_sites(self):
		sitelist = ''
		if os.path.isdir('/var/webapps/owncloud'):
			if os.path.exists('/var/webapps/owncloud/.genesis'):
				f = open('/var/webapps/owncloud/.genesis', 'r')
				try:
					sitelist = ast.literal_eval(f.read())
				except:
					pass
				f.close()
		return sitelist

	def get_info(self):
		return {
			'name': 'ownCloud',
			'short': 'Host your calendar, contacts, photos, files and more',
			'long': ('ownCloud gives you universal access to your files '
					'through a web interface or WebDAV. It also provides a '
					'platform to easily view & sync your contacts, '
					'calendars and bookmarks across all your devices and '
					'enables basic editing right on the web. Installation '
					'has minimal server requirements, doesn\'t need special '
					'permissions and is quick. ownCloud is extendable via a '
					'simple but powerful API for applications and plugins.'),
			'site': 'http://owncloud.org',
			'logo': True
		}
