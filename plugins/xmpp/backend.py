import os
import re
import urllib

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.plugins.core.api import ISSLPlugin
from genesis.utils import shell_cs


class XMPPConfig(Plugin):
    implements(IConfigurable)
    name = 'XMPP'
    id = 'xmpp'
    iconfont = 'gen-bubbles'

    def load(self):
        s = ConfManager.get().load('xmpp', '/etc/prosody/prosody.cfg.lua')
        self.config = self.loads(s)

    def save(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        wasrunning = False
        s = self.dumps(self.config)
        if self.mgr.get_status('prosody') == 'running':
            wasrunning = True
            self.mgr.stop('prosody')
        ConfManager.get().save('xmpp', self.configFile, s)
        ConfManager.get().commit('xmpp')
        if wasrunning:
            self.mgr.start('prosody')

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value

    def items(self):
        return self.config.items()

    def __init__(self):
        #self.configFile = self.app.get_config(self).cfg_file
        self.configFile = '/etc/prosody/prosody.cfg.lua'
        self.config = {}

    def list_files(self):
        return [self.configFile]

    def domains(self):
        d = []
        for x in self.config:
            if x.startswith('_VirtualHost'):
                d.append(x.split('_VirtualHost_')[1])
        return d

    def loads(self, data):
        # Decode the Prosody lua configuration to a manageable Python object
        conf = {}
        active = []
        for line in data.split('\n'):
            # Get rid of comments
            if re.match('.*--.*', line):
                line = line.split('--')[0]
                if not line.split():
                    continue
            # Close any objects if necessary
            if line and active and active[-1].startswith('_') \
            and not re.match('^\t', line):
                active.pop()
            # Arrays and linked lists
            if re.match('\s*(.+)\s*=\s*{', line):
                val = re.match('\s*(.+)\s*=\s*{', line).group(1).split()[0]
                if active:
                    conf[active[-1]][val] = {}
                else:
                    conf[val] = {}
                active.append(val)
            # Base-level variable or keyed list item
            elif re.match('.*\s*=\s*.*', line):
                name, val = re.match('.*(?:^|^\s*|{\s*)(\S+)\s=\s(.+)', line).group(1,2)
                name, val = name.split()[0], val.split()[0].rstrip(';')
                val = re.sub(r'"', '', val)
                if val == 'true':
                    val = True
                elif val == 'false':
                    val = False
                if active and active[-1].startswith('_'):
                    conf[active[-1]][name] = val
                elif active and len(active) >= 2 and active[-2].startswith('_'):
                    conf[active[-2]][active[-1]][name] = val
                elif active:
                    conf[active[-1]][name] = val
                else:
                    conf[name] = val
            # Objects (VirtualHosts)
            elif re.match('\s*(.+) "(.+)"$', line):
                name, val = re.match('\s*(.+) "(.+)"', line).group(1,2)
                name, val = name.split()[0], val.split()[0]
                conf['_'+name+'_'+val] = {}
                active.append('_'+name+'_'+val)
            # Non-keyed list item
            elif re.match('.*\s*"(.+)";', line):
                val = re.match('.*\s*"(.+)";', line).group(1).split()[0]
                conf[active[-1]][len(conf[active[-1]])] = val
            # Match the end of an array
            if re.match('.*}', line):
                closenum = len(re.findall('}', line))
                while closenum > 0:
                    active.pop()
                    closenum = closenum - 1
        return conf

    def dumps(self, data):
        # Dumps the data back to Lua-readable format and returns as string
        vhosts = ''
        allow_registration = ''
        c2s_require_encryption = ''
        s2s_secure_auth = ''
        for x in data:
            if x.startswith('_VirtualHost'):
                vhosts += 'VirtualHost "%s"\n'%x.split('_')[2]
                for y in data[x]:
                    if type(data[x][y]) == dict:
                        vhosts += '\t%s = {\n' % y
                        for z in data[x][y]:
                            vhosts += '\t\t%s = "%s";\n' % (z, data[x][y][z])
                        vhosts += '\t}\n'
                    elif type(data[x][y]) == bool:
                        vhosts += '\t%s = %s\n' % (y, 'true' if data[x][y] else 'false')
                    else:
                        vhosts += '\t%s = "%s";\n' % (y, data[x][y])
                vhosts += '\n'
            elif x == 'allow_registration':
                allow_registration = 'true' if data[x] else 'false'
            elif x == 'c2s_require_encryption':
                c2s_require_encryption = 'true' if data[x] else 'false'
            elif x == 's2s_secure_auth':
                s2s_secure_auth = 'true' if data[x] else 'false'
        cfgfile = (
            '-- Prosody Example Configuration File\n'
            '--\n'
            '-- Information on configuring Prosody can be found on our\n'
            '-- website at http://prosody.im/doc/configure\n'
            '--\n'
            '-- Tip: You can check that the syntax of this file is correct\n'
            '-- when you have finished by running: luac -p prosody.cfg.lua\n'
            '-- If there are any errors, it will let you know what and where\n'
            '-- they are, otherwise it will keep quiet.\n'
            '--\n'
            '-- The only thing left to do is rename this file to remove the .dist ending, and fill in the\n'
            '-- blanks. Good luck, and happy Jabbering!\n'
            '\n'
            'daemonize = true\n'
            'pidfile = "/run/prosody/prosody.pid"\n'
            '\n'
            '---------- Server-wide settings ----------\n'
            '-- Settings in this section apply to the whole server and are the default settings\n'
            '-- for any virtual hosts\n'
            '\n'
            '-- This is a (by default, empty) list of accounts that are admins\n'
            '-- for the server. Note that you must create the accounts separately\n'
            '-- (see http://prosody.im/doc/creating_accounts for info)\n'
            '-- Example: admins = { "user1@example.com", "user2@example.net" }\n'
            'admins = { }\n'
            '\n'
            '-- Enable use of libevent for better performance under high load\n'
            '-- For more information see: http://prosody.im/doc/libevent\n'
            '--use_libevent = true;\n'
            '\n'
            '-- This is the list of modules Prosody will load on startup.\n'
            '-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.\n'
            '-- Documentation on modules can be found at: http://prosody.im/doc/modules\n'
            'modules_enabled = {\n'
            '\n'
            '\t-- Generally required\n'
            '\t\t"roster"; -- Allow users to have a roster. Recommended ;)\n'
            '\t\t"saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.\n'
            '\t\t"tls"; -- Add support for secure TLS on c2s/s2s connections\n'
            '\t\t"dialback"; -- s2s dialback support\n'
            '\t\t"disco"; -- Service discovery\n'
            '\n'
            '\t-- Not essential, but recommended\n'
            '\t\t"private"; -- Private XML storage (for room bookmarks, etc.)\n'
            '\t\t"vcard"; -- Allow users to set vCards\n'
            '\n'
            '\t-- These are commented by default as they have a performance impact\n'
            '\t\t--"privacy"; -- Support privacy lists\n'
            '\t\t--"compression"; -- Stream compression\n'
            '\n'
            '\t-- Nice to have\n'
            '\t\t"version"; -- Replies to server version requests\n'
            '\t\t"uptime"; -- Report how long server has been running\n'
            '\t\t"time"; -- Let others know the time here on this server\n'
            '\t\t"ping"; -- Replies to XMPP pings with pongs\n'
            '\t\t"pep"; -- Enables users to publish their mood, activity, playing music and more\n'
            '\t\t"register"; -- Allow users to register on this server using a client and change passwords\n'
            '\n'
            '\t-- Admin interfaces\n'
            '\t\t"admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands\n'
            '\t\t--"admin_telnet"; -- Opens telnet console interface on localhost port 5582\n'
            '\n'
            '\t-- HTTP modules\n'
            '\t\t--"bosh"; -- Enable BOSH clients, aka "Jabber over HTTP"\n'
            '\t\t--"http_files"; -- Serve static files from a directory over HTTP\n'
            '\n'
            '\t-- Other specific functionality\n'
            '\t\t"posix"; -- POSIX functionality, sends server to background, enables syslog, etc.\n'
            '\t\t--"groups"; -- Shared roster support\n'
            '\t\t--"announce"; -- Send announcement to all online users\n'
            '\t\t--"welcome"; -- Welcome users who register accounts\n'
            '\t\t--"watchregistrations"; -- Alert admins of registrations\n'
            '\t\t--"motd"; -- Send a message to users when they log in\n'
            '\t\t--"legacyauth"; -- Legacy authentication. Only used by some old clients and bots.\n'
            '};\n'          
            '\n'
            '-- These modules are auto-loaded, but should you want\n'
            '-- to disable them then uncomment them here:\n'
            'modules_disabled = {\n'
            '\t-- "offline"; -- Store offline messages\n'
            '\t-- "c2s"; -- Handle client connections\n'
            '\t-- "s2s"; -- Handle server-to-server connections\n'
            '};\n'
            '\n'
            '-- Disable account creation by default, for security\n'
            '-- For more information see http://prosody.im/doc/creating_accounts\n'
            'allow_registration = '+allow_registration+';\n'
            '\n'
            '-- These are the SSL/TLS-related settings. If you don\'t want\n'
            '-- to use SSL/TLS, you may comment or remove this\n'
            'ssl = {\n'
            '\tkey = "/etc/prosody/certs/localhost.key";\n'
            '\tcertificate = "/etc/prosody/certs/localhost.crt";\n'
            '}\n'
            '\n'
            '-- Force clients to use encrypted connections? This option will\n'
            '-- prevent clients from authenticating unless they are using encryption.\n'
            '\n'
            'c2s_require_encryption = false\n'
            '\n'
            '-- Force certificate authentication for server-to-server connections?\n'
            '-- This provides ideal security, but requires servers you communicate\n'
            '-- with to support encryption AND present valid, trusted certificates.\n'
            '-- NOTE: Your version of LuaSec must support certificate verification!\n'
            '-- For more information see http://prosody.im/doc/s2s#security\n'
            '\n'
            's2s_secure_auth = false\n'
            '\n'
            '-- Many servers don\'t support encryption or have invalid or self-signed\n'
            '-- certificates. You can list domains here that will not be required to\n'
            '-- authenticate using certificates. They will be authenticated using DNS.\n'
            '\n'
            '--s2s_insecure_domains = { "gmail.com" }\n'
            '\n'
            '-- Even if you leave s2s_secure_auth disabled, you can still require valid\n'
            '-- certificates for some domains by specifying a list here.\n'
            '\n'
            '--s2s_secure_domains = { "jabber.org" }\n'
            '\n'
            '-- Select the authentication backend to use. The \'internal\' providers\n'
            '-- use Prosody\'s configured data storage to store the authentication data.\n'
            '-- To allow Prosody to offer secure authentication mechanisms to clients, the\n'
            '-- default provider stores passwords in plaintext. If you do not trust your\n'
            '-- server please see http://prosody.im/doc/modules/mod_auth_internal_hashed\n'
            '-- for information about using the hashed backend.\n'
            '\n'
            'authentication = "internal_plain"\n'
            '\n'
            '-- Select the storage backend to use. By default Prosody uses flat files\n'
            '-- in its configured data directory, but it also supports more backends\n'
            '-- through modules. An "sql" backend is included by default, but requires\n'
            '-- additional dependencies. See http://prosody.im/doc/storage for more info.\n'
            '\n'
            '--storage = "sql" -- Default is "internal"\n'
            '\n'
            '-- For the "sql" backend, you can uncomment *one* of the below to configure:\n'
            '--sql = { driver = "SQLite3", database = "prosody.sqlite" } -- Default. \'database\' is the filename.\n'
            '--sql = { driver = "MySQL", database = "prosody", username = "prosody", password = "secret", host = "localhost" }\n'
            '--sql = { driver = "PostgreSQL", database = "prosody", username = "prosody", password = "secret", host = "localhost" }\n'
            '\n'
            '-- Logging configuration\n'
            '-- For advanced logging see http://prosody.im/doc/logging\n'
            'log = {\n'
            '\t-- info = "prosody.log"; -- Change \'info\' to \'debug\' for verbose logging\n'
            '\t-- error = "prosody.err";\n'
            '\t"*syslog"; -- Uncomment this for logging to syslog\n'
            '\t-- "*console"; -- Log to the console, useful for debugging with daemonize=false\n'
            '}\n'
            '\n'
            '----------- Virtual hosts -----------\n'
            '-- You need to add a VirtualHost entry for each domain you wish Prosody to serve.\n'
            '-- Settings under each VirtualHost entry apply *only* to that host.\n'
            '\n'+vhosts+
            '------ Components ------\n'
            '-- You can specify components to add hosts that provide special services,\n'
            '-- like multi-user conferences, and transports.\n'
            '-- For more information on components, see http://prosody.im/doc/components\n'
            '\n'
            '---Set up a MUC (multi-user chat) room server on conference.example.com:\n'
            '--Component "conference.example.com" "muc"\n'
            '\n'
            '-- Set up a SOCKS5 bytestream proxy for server-proxied file transfers:\n'
            '--Component "proxy.example.com" "proxy65"\n'
            '\n'
            '---Set up an external component (default component port is 5347)\n'
            '--\n'
            '-- External components allow adding various services, such as gateways/\n'
            '-- transports to other networks like ICQ, MSN and Yahoo. For more info\n'
            '-- see: http://prosody.im/doc/components#adding_an_external_component\n'
            '--\n'
            '--Component "gateway.example.com"\n'
            '--  component_secret = "password"\n'
        )
        return cfgfile


class XMPPUserControl:
    def list_users(self):
        users = []
        if not os.path.exists('/var/lib/prosody'):
            os.mkdir('/var/lib/prosody')
        for x in os.listdir('/var/lib/prosody'):
            for y in os.listdir(os.path.join('/var/lib/prosody', x, 'accounts')):
                users.append((y.split('.dat')[0], urllib.unquote(x)))
        return sorted(users, key=lambda x: x[0])

    def list_domains(self):
        return [urllib.unquote(x) for x in os.listdir('/var/lib/prosody')]

    def add_user(self, name, dom, passwd):
        x = shell_cs('echo -e "%s\n%s\n" | prosodyctl adduser %s@%s' % (passwd,passwd,name,dom))
        if x[0] != 0:
            raise Exception('XMPP Add user failed: %s' % x[1])

    def del_user(self, name, dom):
        x = shell_cs('prosodyctl deluser %s@%s' % (name,dom))
        if x[0] != 0:
            raise Exception('XMPP Delete user failed: %s' % x[1])

    def chpasswd(self, name, dom, passwd):
        x = shell_cs('echo -e "%s\n%s\n" | prosodyctl passwd %s@%s' % (passwd,passwd,name,dom))
        if x[0] != 0:
            raise Exception('XMPP Password change failed: %s' % x[1])


class XMPPSSLPlugin(Plugin):
    implements(ISSLPlugin)
    pid = 'xmpp'
    text = 'XMPP Chat'
    iconfont = 'gen-bubbles'
    cert_type = 'cert-key'

    def enable_ssl(self, cert, key):
        config = XMPPConfig(self.app)
        config.load()
        config.config['ssl'] = {'certificate': cert, 'key': key}
        config.save()

    def disable_ssl(self):
        config = XMPPConfig(self.app)
        config.load()
        config.config['ssl'] = {}
        config.save()


#class GeneralConfig(ModuleConfig):
#    target=XMPPConfig
#    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']
#
#    labels = {
#        'cfg_file': 'Configuration file'
#    }
#
#    cfg_file = '/etc/prosody/prosody.cfg.lua'
