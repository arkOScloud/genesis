from hashlib import sha1
from base64 import b64encode
from passlib.hash import sha512_crypt, bcrypt
import syslog
import time

from genesis.api import get_environment_vars


def check_password(passw, hash):
    """
    Tests if a password is the same as the hash.

    Instance vars:

    - ``passw`` - ``str``, The password in it's original form
    - ``hash`` - ``str``, The hashed version of the password to check against
    """
    if hash.startswith('{SHA}'):
        try:
            import warnings
            warnings.warn(
                'SHA1 as a password hash may be removed in a future release.')
            passw_hash = '{SHA}' + b64encode(sha1(passw).digest())
            if passw_hash == hash:
                return True
        except:
            import traceback
            traceback.print_exc()
    elif hash.startswith('$2a$') and len(hash) == 60:
        return bcrypt.verify(passw, hash)
    elif sha512_crypt.identify(hash):
        return sha512_crypt.verify(passw, hash)
    return False

class AuthManager(object):
    """
    Authentication middleware which takes care of user authentication

    Instance vars:

    - ``user`` - `str`, current user logged in or None
    """

    def __init__(self, config, app, dispatcher):
        self.user = None

        self.app = app
        app.auth = self
        self._dispatcher = dispatcher
        self._log = config.get('log_facility')

        self._config = config
        self._enabled = False
        if config.has_option('genesis', 'auth_enabled'):
            if config.getint('genesis', 'auth_enabled'):
                # Check for 'users' section
                if config.has_section('users'):
                    if len(config.items('users')) > 0:
                        self._enabled = True
                    else:
                        self._log.error('Authentication requested, but no users configured')
                else:
                    self._log.error('Authentication requested, but no [users] section')

    def deauth(self):
        """
        Deauthenticates current user.
        """
        self.app.session['auth.user'] = None

    def __call__(self, environ, start_response):
        session = environ['app.session']

        if environ['PATH_INFO'] == '/auth-redirect':
            start_response('301 Moved Permanently', [('Location', '/')])
            return ''

        self.user = session['auth.user'] if 'auth.user' in session else None
        if not self._enabled:
            self.user = 'anonymous'
        if self.user is not None or environ['PATH_INFO'].startswith('/dl') \
            or environ['PATH_INFO'].startswith('/core'):
            return self._dispatcher(environ, start_response)

        if environ['PATH_INFO'] == '/auth':
            vars = get_environment_vars(environ)
            user = vars.getvalue('username', '')
            if self._config.has_option('users', user):
                pwd = self._config.get('users', user)
                resp = vars.getvalue('response', '')
                if check_password(resp, pwd):
                    syslog.syslog('session opened for user %s from %s' % (user, environ['REMOTE_ADDR']))
                    session['auth.user'] = user
                    start_response('200 OK', [
                        ('Content-type','text/plain'),
                        ('X-Genesis-Auth', 'ok'),
                    ])
                    return ''

            syslog.syslog('login failed for user %s from %s' % (user, environ['REMOTE_ADDR']))
            time.sleep(4)

            start_response('403 Login Failed', [
                ('Content-type','text/plain'),
                ('X-Genesis-Auth', 'fail'),
            ])
            return 'Login failed'

        templ = self.app.get_template('auth.xml')
        start_response('200 OK', [('Content-type','text/html')])
        start_response('200 OK', [
            ('Content-type','text/html'),
            ('X-Genesis-Auth', 'start'),
        ])
        return templ.render()
