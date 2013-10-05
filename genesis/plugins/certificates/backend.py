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
				'domain': cfg.get('cert', 'domain'),
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
		cfg.set('cert', 'assign', '\n'.join(assign))
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def gencert(self, name, vars):
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
		if vars.getvalue('certcountry', '') != '':
			crt.get_subject().C = vars.getvalue('certcountry')
		if vars.getvalue('certsp', '') != '':
			crt.get_subject().ST = vars.getvalue('certsp')
		if vars.getvalue('certlocale', '') != '':
			crt.get_subject().L = vars.getvalue('certlocale')
		if vars.getvalue('certcn', '') != '':
			crt.get_subject().CN = vars.getvalue('certcn')
		if vars.getvalue('certemail', '') != '':
			crt.get_subject().emailAddress = vars.getvalue('certemail')
		crt.set_serial_number(int(SystemTime().get_serial_time()))
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
		cfg.set('cert', 'domain', crt.get_subject().CN)
		cfg.set('cert', 'assign', '')
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def assign(self, name, assign):
		# Assign a certificate to plugins/webapps as listed
		cfg = ConfigParser.ConfigParser()
		cfg.read('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		alist = cfg.get('cert', 'assign').split('\n')
		for i in alist:
			if i == '':
				alist.remove(i)
		for x in assign:
			if x[0] == 'genesis':
				self.app.gconfig.set('genesis', 'cert_file', 
					'/etc/ssl/certs/genesis/'+name+'.crt')
				self.app.gconfig.set('genesis', 'cert_key', 
					'/etc/ssl/private/genesis/'+name+'.key')
				self.app.gconfig.set('genesis', 'ssl', '1')
				alist.append('Genesis SSL')
				self.app.gconfig.save()
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

	def unassign(self, name, assign):
		cfg = ConfigParser.ConfigParser()
		cfg.read('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		alist = cfg.get('cert', 'assign').split('\n')
		for i in alist:
			if i == '':
				alist.remove(i)
		for x in assign:
			if x[0] == 'genesis':
				self.app.gconfig.set('genesis', 'cert_file', '')
				self.app.gconfig.set('genesis', 'cert_key', '')
				self.app.gconfig.set('genesis', 'ssl', '0')
				alist.remove('Genesis SSL')
				self.app.gconfig.save()
			elif x[0] == 'webapp':
				WebappControl(self.app).ssl_disable(x[1])
				alist.remove(x[1]['name'] + ' ('+x[1]['type']+')')
			elif x[0] == 'plugin':
				x[1].disable_ssl()
				alist.remove(x[1].text)
		cfg.set('cert', 'assign', '\n'.join(alist))
		cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))

	def remove_notify(self, name):
		# Called by plugin when removed.
		# Removes the associated entry from gcinfo tracker file
		try:
			cfg = ConfigParser.ConfigParser()
			cfg.read('/etc/ssl/certs/genesis/'+name+'.gcinfo')
			alist = []
			for x in cfg.get('cert', 'assign').split('\n'):
				if x != name:
					alist.append(x)
			cfg.set('cert', 'assign', '\n'.join(alist))
			cfg.write(open('/etc/ssl/certs/genesis/'+name+'.gcinfo', 'w'))
		except:
			pass

	def remove(self, name):
		# Remove cert, key and control file for associated name
		cfg = ConfigParser.ConfigParser()
		cfg.read('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		alist = cfg.get('cert', 'assign').split('\n')
		wal, pal = self.get_ssl_capable()
		for x in wal:
			if (x['name']+' ('+x['type']+')') in alist:
				WebappControl(self.app).ssl_disable(x)
		for y in pal:
			if y.text in alist:
				y.disable_ssl()
		if 'Genesis SSL' in alist:
			self.app.gconfig.set('genesis', 'cert_file', '')
			self.app.gconfig.set('genesis', 'cert_key', '')
			self.app.gconfig.set('genesis', 'ssl', '0')
			self.app.gconfig.save()
		os.unlink('/etc/ssl/certs/genesis/'+name+'.gcinfo')
		try:
			os.unlink('/etc/ssl/certs/genesis/'+name+'.crt')
		except:
			pass
		try:
			os.unlink('/etc/ssl/private/genesis/'+name+'.key')
		except:
			pass
