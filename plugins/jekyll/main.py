from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs

import re
import nginx
import os


class Jekyll(Plugin):
	implements(apis.webapps.IWebapp)

	addtoblock = []

	def pre_install(self, name, vars):
		rubyctl = apis.langassist(self.app).get_interface('Ruby')
		rubyctl.install_gem('jekyll', 'rdiscount')

	def post_install(self, name, path, vars, dbinfo={}):
		# Make sure the webapps config points to the _site directory and generate it.
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', name))
		for x in c.servers:
			if x.filter('Key', 'root'):
				x.filter('Key', 'root')[0].value = os.path.join(path, '_site')
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', name))
		s = shell_cs('jekyll build --source '+path+' --destination '+os.path.join(path, '_site'), stderr=True)
		if s[0] != 0:
			raise Exception('Jekyll failed to build: %s'%str(s[1]))

		# Return an explicatory message.
		return 'Jekyll has been setup, with a sample site at '+path+'. Modify these files as you like. To learn how to use Jekyll, visit http://jekyllrb.com/docs/usage. After making changes, click the Configure button next to the site, then "Regenerate Site" to bring your changes live.'

	def pre_remove(self, site):
		pass

	def post_remove(self, site):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def regenerate_site(self, site):
		s = shell_cs('jekyll build --source '+site.path.rstrip('_site')+' --destination '+os.path.join(site.path), stderr=True)
		if s[0] != 0:
			raise Exception('Jekyll failed to build: %s'%str(s[1]))
