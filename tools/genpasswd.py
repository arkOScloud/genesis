#!/usr/bin/env python2

import getpass
import sys
from hashlib import sha1
from base64 import b64encode
from passlib.hash import sha512_crypt, bcrypt

def hashpw(passw, scheme = 'sha512_crypt'):
    """
    Returns a hashed form of given password. Default scheme is
    sha512_crypt. Accepted schemes: sha512_crypt, bcrypt, sha (deprecated)
    """
    if scheme == 'sha512_crypt':
        return sha512_crypt.encrypt(passw)
    elif scheme == 'bcrypt':
        # TODO: rounds should be configurable
        return bcrypt.encrypt(passw, rounds=12)
    # This scheme should probably be dropped to avoid creating new
    # unsaltes SHA1 hashes.
    elif scheme == 'sha':
        import warnings
        warnings.warn(
            'SHA1 as a password hash may be removed in a future release.')
        return '{SHA}' + b64encode(sha1(passw).digest())
    return sha512_crypt.encrypt(passw)

def operate():
    if len(sys.argv) >= 2:
        n = sys.argv[1]
    else:
        sys.stderr.write('Must choose a username\n')
        return
    o = getpass.getpass('Choose a password: ', sys.stderr)
    c = getpass.getpass('Confirm password: ', sys.stderr)
    if o != c:
        sys.stderr.write('Passwords did not match!\n')
        operate()
    else:
        print '%s = %s' % (n, hashpw(o))
        return

if __name__ == '__main__':
    operate()
