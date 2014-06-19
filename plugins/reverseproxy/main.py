from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import nginx
import os


class ReverseProxy(Plugin):
	implements(apis.webapps.IWebapp)

	addtoblock = []

	def pre_install(self, name, vars):
		if vars:
			if not vars.getvalue('rp-type', '') or not vars.getvalue('rp-pass', ''):
				raise Exception('Must enter ReverseProxy type and location to pass to')
			elif vars.getvalue('rp-type') in ['fastcgi', 'uwsgi']:
				self.addtoblock = [nginx.Location(vars.getvalue('rp-lregex', '/'), 
					nginx.Key('%s_pass'%vars.getvalue('rp-type'), 
						'%s'%vars.getvalue('rp-pass')),
					nginx.Key('include', '%s_params'%vars.getvalue('rp-type'))
					)]
			else:
				self.addtoblock = [nginx.Location(vars.getvalue('rp-lregex', '/'), 
					nginx.Key('proxy_pass', '%s'%vars.getvalue('rp-pass')),
					nginx.Key('proxy_redirect', 'off'),
					nginx.Key('proxy_buffering', 'off'),
					nginx.Key('proxy_set_header', 'Host $host')
					)]
			if vars.getvalue('rp-xrip', '') == '1':
				self.addtoblock[0].add(nginx.Key('proxy_set_header', 'X-Real-IP $remote_addr'))
			if vars.getvalue('rp-xff', '') == '1':
				self.addtoblock[0].add(nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'))

	def post_install(self, name, path, vars, dbinfo={}):
		pass

	def pre_remove(self, site):
		pass

	def post_remove(self, site):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass
