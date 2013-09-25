import ntplib
import OpenSSL
import os

from genesis.utils.error import SystemTimeError


class CertControl:

	def gencert(certname, keyname):
		# Make sure our folders are in place
		if not os.path.exists('/etc/ssl/certs/genesis'):
			os.mkdir('/etc/ssl/certs/genesis')
		if not os.path.exists('/etc/ssl/private/genesis'):
			os.mkdir('/etc/ssl/private/genesis')

		# If system time is way off, raise an error
		ntp = ntplib.NTPClient()
		resp = ntp.request('0.pool.ntp.org', version=3)
		if resp.offset < -3600 or resp.offset > 3600:
			raise SystemTimeError(resp.offset)

		# Generate a key, then use it to sign a new cert
		# We'll use 2048-bit RSA until pyOpenSSL supports ECC
		key = OpenSSL.crypto.PKey()
		key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
		crt = OpenSSL.crypto.X509()
		crt.set_serial_number(1)
		crt.gmtime_adj_notBefore(0)
		crt.gmtime_adj_notAfter(2*365*24*60*60)
		crt.set_pubkey(key)
		crt.sign(k, 'sha1')
		open(sslcert, "wt").write(
			OpenSSL.crypto.dump_certificate(
				OpenSSL.crypto.FILETYPE_PEM, 
				'/etc/ssl/certs/genesis/'+crt)
			)
		open(sslkey, "wt").write(
			OpenSSL.crypto.dump_privatekey(
				OpenSSL.crypto.FILETYPE_PEM, 
				'/etc/ssl/private/genesis/'+key)
			)
