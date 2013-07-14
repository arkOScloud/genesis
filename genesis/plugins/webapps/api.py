from genesis.com import *
from genesis import apis

import os
import re


class Webapps(apis.API):
	def __init__(self, app):
		self.app = app

	class IWebapp(Interface):
		name = ''
		dpath = ''
		icon = 'gen-earth'
		php = False
		nomulti = False
		addtoblock = ''

		def pre_install(self, name, vars):
			pass

		def post_install(self, name, path, vars):
			pass

		def pre_remove(self, name, path):
			pass

		def post_remove(self, name):
			pass

		def get_info(self):
			pass

	def get_apptypes(self):
		applist = []
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			applist.append(plugin)
		return applist

	def get_sites(self):
		applist = []
		if not os.path.exists('/etc/nginx/sites-available'):
			os.makedirs('/etc/nginx/sites-available')
		if not os.path.exists('/etc/nginx/sites-enabled'):
			os.makedirs('/etc/nginx/sites-enabled')

		for site in os.listdir('/etc/nginx/sites-available'):
			# Set default values and regexs to use
			addr = False
			port = '80'
			php = False
			stype = 'Unknown'
			path = os.path.join('/etc/nginx/sites-available', site)
			rtype = re.compile('.*?# GENESIS ((?:[a-z][a-z]+))', flags=re.IGNORECASE)
			rport = re.compile('.*?listen (\\d+)\s*(.*?);')
			raddr = re.compile('.*?server_name ([^\s]+).*?;', flags=re.IGNORECASE)
			rpath = re.compile('.*?root ((?:\\/[\\w\\.\\-]+)+).*?;', flags=re.IGNORECASE)
			rphp = re.compile('.*?index .*?php.*?;', flags=re.IGNORECASE)

			# Get actual values
			f = open(os.path.join('/etc/nginx/sites-available', site), 'r')
			for line in f.readlines():
				if re.match(rtype, line):
					stype = re.match(rtype, line).group(1)
				elif re.match(rport, line):
					port = re.match(rport, line).group(1)
				elif re.match(raddr, line):
					addr = re.match(raddr, line).group(1)
				elif re.match(rpath, line):
					path = re.match(rpath, line).group(1)
				elif re.match(rphp, line):
					php = True
			if os.path.exists(os.path.join('/etc/nginx/sites-enabled', site)):
				enabled = True
			else:
				enabled = False

			# Create dict of values
			applist.append({
					'name': site,
					'type': stype,
					'addr': addr, 
					'port': port,
					'path': path, 
					'php': php,
					'class': self.get_interface(stype),
					'enabled': enabled
				})
			f.close()
		return applist

	def get_interface(self, name):
		interface = ''
		for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
			if plugin.__class__.__name__ == name:
				interface = plugin
		return interface
