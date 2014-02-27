import ConfigParser
import nginx
import os

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.plugins.users.backend import *
from genesis.plugins.webapps.backend import WebappControl
from genesis.utils import shell_cs, hashpw


class RadicaleConfig(Plugin):
    implements(IConfigurable)
    name = 'Calendar/Contacts'
    id = 'radicale'
    iconfont = 'gen-calendar'

    def load(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(ConfManager.get().load('radicale', self.configFile))

    def save(self):
        self.config.write(open(self.configFile, 'w'))
        ConfManager.get().commit('radicale')

    def __init__(self):
        self.configFile = self.app.get_config(self).cfg_file
        self.config = None

    def list_files(self):
        return [self.configFile]


class GeneralConfig(ModuleConfig):
    target=RadicaleConfig
    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']

    labels = {
        'cfg_file': 'Configuration file',
        'first_run_complete': 'First Run is complete'
    }

    cfg_file = '/etc/radicale/config'
    first_run_complete = False


class RadicaleControl(Plugin):
    default_config = """
        [server]
        # CalDAV server hostnames separated by a comma
        # IPv4 syntax: address:port
        # IPv6 syntax: [address]:port
        # For example: 0.0.0.0:9999, [::]:9999
        # IPv6 adresses are configured to only allow IPv6 connections
        hosts = 0.0.0.0:5232
        # Daemon flag
        daemon = False
        # File storing the PID in daemon mode
        pid =
        # SSL flag, enable HTTPS protocol
        ssl = False
        # SSL certificate path
        certificate = /etc/apache2/ssl/server.crt
        # SSL private key
        key = /etc/apache2/ssl/server.key
        # Reverse DNS to resolve client address in logs
        dns_lookup = True
        # Root URL of Radicale (starting and ending with a slash)
        base_prefix = /
        # Message displayed in the client when a password is needed
        realm = Radicale - Password Required lol


        [encoding]
        # Encoding for responding requests
        request = utf-8
        # Encoding for storing local collections
        stock = utf-8


        [auth]
        # Authentication method
        # Value: None | htpasswd | IMAP | LDAP | PAM | courier | http
        type = None

        # Usernames used for public collections, separated by a comma
        public_users = public
        # Usernames used for private collections, separated by a comma
        private_users = private
        # Htpasswd filename
        htpasswd_filename = /etc/radicale/users
        # Htpasswd encryption method
        # Value: plain | sha1 | crypt
        htpasswd_encryption = crypt

        # LDAP server URL, with protocol and port
        ldap_url = ldap://localhost:389/
        # LDAP base path
        ldap_base = ou=users,dc=example,dc=com
        # LDAP login attribute
        ldap_attribute = uid
        # LDAP filter string
        # placed as X in a query of the form (&(...)X)
        # example: (objectCategory=Person)(objectClass=User)(memberOf=cn=calenderusers,ou=users,dc=example,dc=org)
        # leave empty if no additional filter is needed
        ldap_filter =
        # LDAP dn for initial login, used if LDAP server does not allow anonymous searches
        # Leave empty if searches are anonymous
        ldap_binddn =
        # LDAP password for initial login, used with ldap_binddn
        ldap_password =
        # LDAP scope of the search
        ldap_scope = OneLevel

        # IMAP Configuration
        imap_hostname = localhost
        imap_port = 143
        imap_ssl = False

        # PAM group user should be member of
        pam_group_membership =

        # Path to the Courier Authdaemon socket
        courier_socket =

        # HTTP authentication request URL endpoint
        http_url =
        # POST parameter to use for username
        http_user_parameter =
        # POST parameter to use for password
        http_password_parameter =


        [rights]
        # Rights management method
        # Value: None | owner_only | owner_write | from_file
        type = None

        # File for rights management from_file
        file = ~/.config/radicale/rights


        [storage]
        # Storage backend
        # Value: filesystem | database
        type = filesystem

        # Folder for storing local collections, created if not present
        filesystem_folder = ~/.config/radicale/collections

        # Database URL for SQLAlchemy
        # dialect+driver://user:password@host/dbname[?key=value..]
        # For example: sqlite:///var/db/radicale.db, postgresql://user:password@localhost/radicale
        # See http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#sqlalchemy.create_engine
        database_url =


        [logging]
        # Logging configuration file
        # If no config is given, simple information is printed on the standard output
        # For more information about the syntax of the configuration file, see:
        # http://docs.python.org/library/logging.config.html
        config = /etc/radicale/logging
        # Set the default logging level to debug
        debug = False
        # Store all environment variables (including those set in the shell)
        full_environment = False


        # Additional HTTP headers
        #[headers]
        #Access-Control-Allow-Origin = *
        """

    def add_user(self, user, passwd):
        ic = []
        if os.path.exists('/etc/radicale/users'):
            for x in open('/etc/radicale/users', 'r').read().split('\n'):
                ic.append(x)
        f = open('/etc/radicale/users', 'w')
        for x in ic:
            f.write(x+'\n')
        f.write('%s:%s'%(user, hashpw(passwd, 'ssha')))
        f.close()

    def edit_user(self, user, passwd):
        ic = []
        if os.path.exists('/etc/radicale/users'):
            for x in open('/etc/radicale/users', 'r').read().split('\n'):
                if not user == x.split(':')[0]:
                    ic.append(x)
        f = open('/etc/radicale/users', 'w')
        for x in ic:
            f.write(x+'\n')
        f.write('%s:%s'%(user, hashpw(passwd, 'ssha')))
        f.close()

    def del_user(self, user):
        ic = []
        if os.path.exists('/etc/radicale/users'):
            for x in open('/etc/radicale/users', 'r').read().split('\n'):
                if not user == x.split(':')[0]:
                    ic.append(x)
        f = open('/etc/radicale/users', 'w')
        for x in ic:
            f.write(x+'\n')
        f.close()

    def list_users(self):
        u = []
        if os.path.exists('/etc/radicale/users'):
            for x in open('/etc/radicale/users', 'r').read().split('\n'):
                if x.split():
                    u.append(x.split(':')[0])
        return u

    def is_installed(self):
        # Verify the different components of the server setup
        if not os.path.exists('/etc/radicale/config') or not os.path.isdir('/usr/lib/radicale') \
        or not os.path.exists('/etc/radicale/radicale.wsgi'):
            return False
        elif not 'radicale' in [x.name for x in apis.webapps(self.app).get_sites()]:
            return False
        return True

    def setup(self, addr, port):
        # Make sure Radicale is installed and ready
        pyctl = apis.langassist(self.app).get_interface('Python')
        users = UsersBackend(self.app)
        if not pyctl.is_installed('radicale'):
            pyctl.install('radicale')
        if not pyctl.is_installed('uWSGI'):
            pyctl.install('uwsgi')
        if not os.path.exists('/etc/radicale/config'):
            if not os.path.isdir('/etc/radicale'):
                os.mkdir('/etc/radicale')
            open('/etc/radicale/config', 'w').write(self.default_config)
        if not os.path.isdir('/usr/lib/radicale'):
            os.mkdir('/usr/lib/radicale')
        # Add the site process
        users.add_user('radicale')
        users.add_group('radicale')
        users.add_to_group('radicale', 'radicale')
        wsgi_file = 'import radicale\n'
        wsgi_file += 'radicale.log.start()\n'
        wsgi_file += 'application = radicale.Application()\n'
        open('/etc/radicale/radicale.wsgi', 'w').write(wsgi_file)
        s = apis.orders(self.app).get_interface('supervisor')
        if s:
            s[0].order('new', 'radicale', 'program', 
                [('directory', '/etc/radicale'), ('user', 'radicale'), 
                ('command', 'uwsgi -s /tmp/radicale.sock -C --wsgi-file radicale.wsgi'),
                ('stdout_logfile', '/var/log/radicale.log'),
                ('stderr_logfile', '/var/log/radicale.log')])
        block = [
            nginx.Location('/',
                nginx.Key('auth_basic', '"Genesis Calendar Server (Radicale)"'),
                nginx.Key('auth_basic_user_file', '/etc/radicale/users'),
                nginx.Key('include', 'uwsgi_params'),
                nginx.Key('uwsgi_pass', 'unix:///tmp/radicale.sock'),
            )
        ]
        if not os.path.exists('/etc/radicale/users'):
            open('/etc/radicale/users', 'w').write('')
        WebappControl(self.app).add_reverse_proxy('radicale', 
            '/usr/lib/radicale', addr, port, block)
        apis.networkcontrol(self.app).add_webapp(('radicale', 'ReverseProxy', port))
        c = self.app.get_config(RadicaleConfig(self.app))
        c.first_run_complete = True
        c.save()
