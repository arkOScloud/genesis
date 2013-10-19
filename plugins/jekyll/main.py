from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, download

import re
import os


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
		# Make sure Ruby directory is in the PATH.
		# This should work until there is a viable Ruby (RVM) plugin for Genesis
		profile = []
		f = open('/etc/profile', 'r')
		for l in f.readlines():
			if l.startswith('PATH="') and not 'ruby/2.0.0/bin' in l:
				l = l.rstrip('"\n')
				l += ':/root/.gem/ruby/2.0.0/bin"\n'
				profile.append(l)
				os.environ['PATH'] = os.environ['PATH'] + ':/root/.gem/ruby/2.0.0/bin'
			else:
				profile.append(l)
		f.close()
		open('/etc/profile', 'w').writelines(profile)

		# Install the Jekyll and rdiscount gems required.
		if not any('jekyll' in s for s in shell('gem list').split('\n')):
			shell('gem install jekyll')
		if not any('rdiscount' in s for s in shell('gem list').split('\n')):
			shell('gem install rdiscount')

	def post_install(self, name, path, vars):
		# Make sure the webapps config points to the _site directory and generate it.
		shell('sed -i "s/.*root .*/   root %s\;/" /etc/nginx/sites-available/%s' % (re.escape(path+'/_site'), name))
		shell('jekyll build --source '+path+' --destination '+path+'/_site')

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
		shell('jekyll build --source '+site['path'].rstrip('_site')+' --destination '+os.path.join(site['path']))

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
