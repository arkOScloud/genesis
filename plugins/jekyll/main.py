from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, download

import re
import nginx
import os


class Jekyll(Plugin):
	implements(apis.webapps.IWebapp)

	addtoblock = []

	def pre_install(self, name, vars):
		rubyctl = apis.langassist(self.app).get_interface('Ruby')
		rubyctl.install_gem('jekyll', 'rdiscount')

	def post_install(self, name, path, vars):
		# Make sure the webapps config points to the _site directory and generate it.
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', name))
		c.servers[0].filter('Key', 'root')[0].value = os.path.join(path, '_site')
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', name))
		shell('jekyll build --source '+path+' --destination '+os.path.join(path, '_site'))

		# Return an explicatory message.
		return 'Jekyll has been setup, with a sample site at '+path+'. Modify these files as you like. To learn how to use Jekyll, visit http://jekyllrb.com/docs/usage. After making changes, click the Configure button next to the site, then "Regenerate Site" to bring your changes live.'

	def pre_remove(self, name, path):
		pass

	def post_remove(self, name):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def regenerate_site(self, site):
		shell('jekyll build --source '+site.path.rstrip('_site')+' --destination '+os.path.join(site.path))
