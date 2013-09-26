import ConfigParser
import glob
import OpenSSL
import os

from genesis import apis
from genesis.com import *
from genesis.utils import SystemTime
from genesis.utils.error import SystemTimeError
from genesis.plugins.core.api import ISSLPlugin
from genesis.plugins.webapps.backend import WebappControl

class CertControl(Plugin):
	def get_certs(self):
		# Find all certs added by Genesis and return basic information
		certs = []
		if not os.path.exists('/etc/ssl/certs/genesis'):
			os.mkdir('/etc/ssl/certs/genesis')
		if not os.path.exists('/etc/ssl/private/genesis'):
			os.mkdir('/etc/ssl/private/genesis')
		for x in glob.glob('/etc/ssl/certs/genesis/*.gcinfo'):
			cfg = ConfigParser.ConfigParser()
			cfg.read(x)
			certs.append({'name': cfg.get('cert', 'name'),
				'expiry': cfg.get('cert', 'expiry'),
				'chain': cfg.get('cert', 'chain'),
				'assign': cfg.get('cert', 'assign').split('\n')})
		return certs

	def get_ssl_capable(self):
		lst = []
		for x in apis.webapps(self.app).get_sites():
			if x['ssl_able']:
				lst.append(x)
		return lst, self.app.grab_plugins(ISSLPlugin)

	def has_expired(self, certname):
		# Return True if the plugin is expired, False if not
		c = open('/etc/ssl/certs/genesis/'+certname+'.crt', 'r').read()
		crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, c)
		return crt.has_expired()

	def add_ext_cert(self, name, chain='', assign=[]):
		# Add a .gcinfo file for a certificate uploaded externally
		# TODO accept and write file objs
		c = open('/etc/ssl/certs/genesis/'+name+'.crt', 'r').read()
		crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, c)
		cfg = ConfigParser.ConfigParser()
		cfg.add_section('cert')
		cfg.set('cert', 'name', name)
		cfg.set('cert', 'expiry', crt.get_notAfter())
		cfg.set('cert', 'chain', chain)
		cfg.set('cert', 'assigned', '\n'.join(assign))
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def gencert(self, name):
		# Make sure our folders are in place
		if not os.path.exists('/etc/ssl/certs/genesis'):
			os.mkdir('/etc/ssl/certs/genesis')
		if not os.path.exists('/etc/ssl/private/genesis'):
			os.mkdir('/etc/ssl/private/genesis')

		# If system time is way off, raise an error
		st = SystemTime().get_offset()
		if st < -3600 or st > 3600:
			raise SystemTimeError(st)

		# Generate a key, then use it to sign a new cert
		# We'll use 2048-bit RSA until pyOpenSSL supports ECC
		key = OpenSSL.crypto.PKey()
		key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
		crt = OpenSSL.crypto.X509()
		crt.set_serial_number(1)
		crt.gmtime_adj_notBefore(0)
		crt.gmtime_adj_notAfter(2*365*24*60*60)
		crt.set_pubkey(key)
		crt.sign(key, 'sha1')
		open('/etc/ssl/certs/genesis/'+name+'.crt', "wt").write(
			OpenSSL.crypto.dump_certificate(
				OpenSSL.crypto.FILETYPE_PEM, crt)
			)
		os.chmod('/etc/ssl/certs/genesis/'+name+'.crt', 0660)
		open('/etc/ssl/private/genesis/'+name+'.key', "wt").write(
			OpenSSL.crypto.dump_privatekey(
				OpenSSL.crypto.FILETYPE_PEM, key)
			)
		os.chmod('/etc/ssl/private/genesis/'+name+'.key', 0660)

		cfg = ConfigParser.ConfigParser()
		cfg.add_section('cert')
		cfg.set('cert', 'name', name)
		cfg.set('cert', 'expiry', crt.get_notAfter())
		cfg.set('cert', 'chain', '')
		cfg.set('cert', 'assign', '')
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def assign(self, name, assign):
		# Assign a certificate to plugins/webapps as listed
		# TODO read the cfg and disable SSL on unselected options
		cfg = ConfigParser.ConfigParser()
		cfg.read('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		alist = []
		for x in assign:
			if x[0] == 'genesis':
				self.app.gconfig.set('genesis', 'cert_file', 
					'/etc/ssl/certs/genesis/'+name+'.crt')
				self.app.gconfig.set('genesis', 'cert_key', 
					'/etc/ssl/private/genesis/'+name+'.key')
				alist.append('Genesis')
			elif x[0] == 'webapp':
				WebappControl(self.app).ssl_enable(x[1],
					'/etc/ssl/certs/genesis/'+name+'.crt',
					'/etc/ssl/private/genesis/'+name+'.key')
				alist.append(x[1]['name'] + ' ('+x[1]['type']+')')
			elif x[0] == 'plugin':
				x[1].enable_ssl()
				alist.append(x[1].text)
		cfg.set('cert', 'assign', '\n'.join(alist))
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def remove(self, name):
		# Remove cert, key and control file for associated name
		os.unlink('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		try:
			os.unlink('/etc/ssl/certs/genesis/'+name+'.crt')
		except:
			pass
		try:
			os.unlink('/etc/ssl/private/genesis/'+name+'.key')
		except:
			pass
