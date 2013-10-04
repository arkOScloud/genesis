from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, download

import re


class Jekyll(Plugin):
	implements(apis.webapps.IWebapp)
	name = 'Jekyll'
	dpath = 'https://uspx.arkos.io/resources/jekyll-sample.tar.gz'
	icon = 'gen-earth'
	php = False
	nomulti = False
	ssl = True

	addtoblock = ''

	def pre_install(self, name, vars):
		if not any('jekyll' in s for s in shell('gem list').split('\n')):
			shell('gem install jekyll')
		if not any('rdiscount' in s for s in shell('gem list').split('\n')):
			shell('gem install rdiscount')

	def post_install(self, name, path, vars):
		shell('sed -i "s/.*root .*/   root %s\;/" /etc/nginx/sites-available/%s' % (re.escape(path+'/_site'), name))
		shell('jekyll build --source '+path+' --destination '+path+'/_site')

	def pre_remove(self, name, path):
		pass

	def post_remove(self, name):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def get_info(self):
		return {
			'name': 'Jekyll',
			'short': 'Transform your plain text into static websites and blogs.',
			'long': ('Jekyll is a simple, blog-aware, static site '
				'generator. It takes a template directory containing raw '
				'text files in various formats, runs it through Markdown '
				'(or Textile) and Liquid converters, and spits out a '
				'complete, ready-to-publish static website suitable for '
				'serving with your favorite web server.'),
			'site': 'http://jekyllrb.com',
			'logo': True
		}
