import ConfigParser
import nginx
import os
import stat

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
    default_config = (
        '[server]\n'
        '# CalDAV server hostnames separated by a comma\n'
        '# IPv4 syntax: address:port\n'
        '# IPv6 syntax: [address]:port\n'
        '# For example: 0.0.0.0:9999, [::]:9999\n'
        '# IPv6 adresses are configured to only allow IPv6 connections\n'
        'hosts = 0.0.0.0:5232\n'
        '# Daemon flag\n'
        'daemon = False\n'
        '# File storing the PID in daemon mode\n'
        'pid =\n'
        '# SSL flag, enable HTTPS protocol\n'
        'ssl = False\n'
        '# SSL certificate path\n'
        'certificate = /etc/apache2/ssl/server.crt\n'
        '# SSL private key\n'
        'key = /etc/apache2/ssl/server.key\n'
        '# Reverse DNS to resolve client address in logs\n'
        'dns_lookup = True\n'
        '# Root URL of Radicale (starting and ending with a slash)\n'
        'base_prefix = /\n'
        '# Message displayed in the client when a password is needed\n'
        'realm = Radicale - Password Required lol\n'
        '\n'
        '\n'
        '[encoding]\n'
        '# Encoding for responding requests\n'
        'request = utf-8\n'
        '# Encoding for storing local collections\n'
        'stock = utf-8\n'
        '\n'
        '\n'
        '[auth]\n'
        '# Authentication method\n'
        '# Value: None | htpasswd | IMAP | LDAP | PAM | courier | http\n'
        'type = None\n'
        '\n'
        '# Usernames used for public collections, separated by a comma\n'
        'public_users = public\n'
        '# Usernames used for private collections, separated by a comma\n'
        'private_users = private\n'
        '# Htpasswd filename\n'
        'htpasswd_filename = /etc/radicale/users\n'
        '# Htpasswd encryption method\n'
        '# Value: plain | sha1 | crypt\n'
        'htpasswd_encryption = crypt\n'
        '\n'
        '# LDAP server URL, with protocol and port\n'
        'ldap_url = ldap://localhost:389/\n'
        '# LDAP base path\n'
        'ldap_base = ou=users,dc=example,dc=com\n'
        '# LDAP login attribute\n'
        'ldap_attribute = uid\n'
        '# LDAP filter string\n'
        '# placed as X in a query of the form (&(...)X)\n'
        '# example: (objectCategory=Person)(objectClass=User)(memberOf=cn=calenderusers,ou=users,dc=example,dc=org)\n'
        '# leave empty if no additional filter is needed\n'
        'ldap_filter =\n'
        '# LDAP dn for initial login, used if LDAP server does not allow anonymous searches\n'
        '# Leave empty if searches are anonymous\n'
        'ldap_binddn =\n'
        '# LDAP password for initial login, used with ldap_binddn\n'
        'ldap_password =\n'
        '# LDAP scope of the search\n'
        'ldap_scope = OneLevel\n'
        '\n'
        '# IMAP Configuration\n'
        'imap_hostname = localhost\n'
        'imap_port = 143\n'
        'imap_ssl = False\n'
        '\n'
        '# PAM group user should be member of\n'
        'pam_group_membership =\n'
        '\n'
        '# Path to the Courier Authdaemon socket\n'
        'courier_socket =\n'
        '\n'
        '# HTTP authentication request URL endpoint\n'
        'http_url =\n'
        '# POST parameter to use for username\n'
        'http_user_parameter =\n'
        '# POST parameter to use for password\n'
        'http_password_parameter =\n'
        '\n'
        '\n'
        '[rights]\n'
        '# Rights management method\n'
        '# Value: None | owner_only | owner_write | from_file\n'
        'type = None\n'
        '\n'
        '# File for rights management from_file\n'
        'file = ~/.config/radicale/rights\n'
        '\n'
        '\n'
        '[storage]\n'
        '# Storage backend\n'
        '# Value: filesystem | database\n'
        'type = filesystem\n'
        '\n'
        '# Folder for storing local collections, created if not present\n'
        'filesystem_folder = ~/.config/radicale/collections\n'
        '\n'
        '# Database URL for SQLAlchemy\n'
        '# dialect+driver://user:password@host/dbname[?key=value..]\n'
        '# For example: sqlite:///var/db/radicale.db, postgresql://user:password@localhost/radicale\n'
        '# See http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#sqlalchemy.create_engine\n'
        'database_url =\n'
        '\n'
        '\n'
        '[logging]\n'
        '# Logging configuration file\n'
        '# If no config is given, simple information is printed on the standard output\n'
        '# For more information about the syntax of the configuration file, see:\n'
        '# http://docs.python.org/library/logging.config.html\n'
        'config = /etc/radicale/logging\n'
        '# Set the default logging level to debug\n'
        'debug = False\n'
        '# Store all environment variables (including those set in the shell)\n'
        'full_environment = False\n'
        '\n'
        '\n'
        '# Additional HTTP headers\n'
        '#[headers]\n'
        '#Access-Control-Allow-Origin = *\n'
        )

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
        if not pyctl.is_installed('Radicale'):
            pyctl.install('radicale')
        # due to packaging bugs, make extra sure perms are readable
        st = os.stat('/usr/lib/python2.7/site-packages/radicale')
        for r, d, f in os.walk('/usr/lib/python2.7/site-packages/radicale'):
            for x in d:
                os.chmod(os.path.join(r, x), st.st_mode&stat.S_IROTH&stat.S_IRGRP)
            for x in f:
                os.chmod(os.path.join(r, x), st.st_mode&stat.S_IROTH&stat.S_IRGRP)
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
        os.chmod('/etc/radicale/radicale.wsgi', 0766)
        s = apis.orders(self.app).get_interface('supervisor')
        if s:
            s[0].order('new', 'radicale', 'program', 
                [('directory', '/etc/radicale'), ('user', 'radicale'), 
                ('command', 'uwsgi -s /tmp/radicale.sock -C --plugin python2 --wsgi-file radicale.wsgi'),
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
            os.chmod('/etc/radicale/users', 0766)
        WebappControl(self.app).add_reverse_proxy('radicale', 
            '/usr/lib/radicale', addr, port, block)
        apis.networkcontrol(self.app).add_webapp(('radicale', 'ReverseProxy', port))
        c = self.app.get_config(RadicaleConfig(self.app))
        c.first_run_complete = True
        c.save()
