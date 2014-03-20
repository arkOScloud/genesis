import os
import re
import hashlib
import random
import stat

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.utils import shell_cs
from genesis.plugins.core.api import ISSLPlugin
from genesis.plugins.users.backend import UsersBackend
from genesis.plugins.network.backend import IHostnameManager


class MailConfig(Plugin):
    implements(IConfigurable)
    name = 'Mailserver'
    id = 'mail'
    iconfont = 'gen-envelop'

    def load(self):
        s = ConfManager.get().load('email', self.postfix_main_file)
        self.postfix_main = self.loads('postfix_main', s)
        s = ConfManager.get().load('email', self.postfix_master_file)
        self.postfix_master = self.loads('postfix_master', s)
        s = ConfManager.get().load('email', self.dovecot_conf_file)
        self.dovecot_conf = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', 
            os.path.join(self.dovecot_conf_dir, '10-auth.conf'))
        self.dovecot_auth = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', 
            os.path.join(self.dovecot_conf_dir, '10-mail.conf'))
        self.dovecot_mail = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', 
            os.path.join(self.dovecot_conf_dir, '10-ssl.conf'))
        self.dovecot_ssl = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', 
            os.path.join(self.dovecot_conf_dir, '10-master.conf'))
        self.dovecot_master = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', 
            os.path.join(self.dovecot_conf_dir, 'auth-sql.conf.ext'))
        self.dovecot_authsql = self.loads('dovecot_conf', s)
        s = ConfManager.get().load('email', '/etc/dovecot/dovecot-sql.conf.ext'))
        self.dovecot_dovecotsql = self.loads('dovecot_conf', s)

    def save(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        wasrunning = False
        s = self.dumps(self.config)
        if self.mgr.get_status('postfix') == 'running':
            wasrunning = True
            self.mgr.stop('postfix')
            self.mgr.stop('dovecot')
        ConfManager.get().save('email', self.configFile, s)
        ConfManager.get().commit('email')
        if wasrunning:
            self.mgr.start('postfix')
            self.mgr.start('dovecot')

    def __init__(self):
        self.postfix_main_file = '/etc/postfix/main.cf'
        self.postfix_master_file = '/etc/postfix/master.cf'
        self.dovecot_conf_file = '/etc/dovecot/dovecot.conf'
        self.dovecot_conf_dir = '/etc/dovecot/conf.d'
        self.postfix_main = {}
        self.postfix_master = []
        self.dovecot_conf = {}
        self.dovecot_auth = {}
        self.dovecot_mail = {}
        self.dovecot_ssl = {}
        self.dovecot_master = {}
        self.dovecot_authsql = {}
        self.dovecot_dovecotsql = {}

    def list_files(self):
        return [self.postfix_main_file, self.postfix_master_file,
            self.dovecot_conf_file, os.path.join(self.dovecot_conf_dir, '*')]

    def loads(self, cfgtype, data):
        # Decode configuration files to a manageable Python object
        if cfgtype == 'postfix_main':
            conf = {}
            lastname = ''
            for line in data.split('\n'):
                if re.match('.*#.*', line):
                    line = line.split('#')[0]
                    if not line.split():
                        continue
                if re.match('^\t.*', line) and lastname:
                    if not type(conf[lastname]) == list:
                        conf[lastname] = []
                    val = re.match('^\s*(.*)$', line).group(1)
                    conf[lastname].append(val)
                elif re.match('.*\s*=\s*.*', line):
                    name, val = re.match('(\S+)\s*=\s*(.*)$', line).group(1,2)
                    name, val = name.split()[0], val.split()[0] if val.split() else ''
                    val = re.sub(r'"', '', val)
                    if ', ' in val:
                        val = val.split(', ')
                    conf[name] = val
                    lastname = name
        elif cfgtype == 'postfix_master':
            conf = []
            lastname = ''
            for line in data.split('\n'):
                if re.match('.*#.*', line):
                    line = line.split('#')[0]
                    if not line.split():
                        continue
                if re.match('^\s*-o.*', line) and lastname:
                    val = re.match('^\s*-o\s*(.*)$', line).group(1)
                    for x in enumerate(conf):
                        if x[1][0] == lastname:
                            conf[x[0]].append(val)
                            break
                elif line.split():
                    conf.append(line.split())
                    lastname = line.split()[0]
        elif cfgtype == 'dovecot_conf':
            conf = {}
            active = []
            for line in data.split('\n'):
                if re.match('.*#.*', line):
                    line = line.split('#')[0]
                    if not line.split():
                        continue
                elif line.startswith('!'):
                    num = 0
                    name, val = re.match('^!(.+)\s*(.+)$', line).group(1,2)
                    if active:
                        for x in conf[active[-1]]:
                            if x.startswith(name+'_'):
                                num = num + 1
                        conf[active[-1]][name] = val
                    else:
                        for x in conf:
                            if x.startswith(name+'_'):
                                num = num + 1
                        conf[name] = val
                elif re.match('\s*(.+)\s*{\s*$', line):
                    val = re.match('\s*(.+)\s*{', line).group(1)
                    num = 0
                    if active:
                        for x in conf[active[-1]]:
                            if x.startswith(val+'_'):
                                num = num + 1
                        conf[active[-1]][val+'_'+str(num)] = {}
                    else:
                        for x in conf:
                            if x.startswith(val+'_'):
                                num = num + 1
                        conf[val+'_'+str(num)] = {}
                    active.append(val)
                elif re.match('.*\s*=\s*.*', line):
                    name, val = re.match('(\S+)\s*=\s*(.*)$', line).group(1,2)
                    name, val = name.split()[0], val.split()[0] if val.split() else ''
                    val = re.sub(r'"', '', val)
                    if ', ' in val:
                        val = val.split(', ')
                    if active:
                        conf[active[-1]][name] = val
                    else:
                        conf[name] = val
                # Match the end of an array
                if re.match('.*}', line):
                    closenum = len(re.findall('}', line))
                    while closenum > 0:
                        active.pop()
                        closenum = closenum - 1
        return conf

    def dumps(self, cfgtype, data):
        f = ''
        if cfgtype == 'postfix_main':
            for x in data:
                if type(data[x]) == str:
                    f += x+' = '+data[x]+'\n'
                else:
                    f += x+' = '+', '.join(data[x])+'\n'
        elif cfgtype == 'postfix_master':
            sp = (' '*7)
            for x in data:
                f += x[0]+sp+x[1]+' '+x[2]+sp+x[3]+sp+x[4]+sp+x[5]+sp+x[6]+sp+x[7]+'\n'
                if len(x) >= 9:
                    for y in x[8:]:
                        f += '  -o '+y+'\n'
        elif cfgtype == 'dovecot_conf':
            for x in data:
                if x.startswith('include'):
                    f += '!'+x.rsplit('_', 1)[0]+' '+data[x]+'\n'
                elif re.match('.*_[0-9]+$', x):
                    f += x.rsplit('_', 1)[0]+' {\n'
                    for y in data[x]:
                        f += '  '+y+' = '+data[x][y]+'\n'
                else:
                    f += x+' = '+data[x]+'\n'
        return f


class EmailControl(Plugin):
    def initial_setup(self):
        # Grab frameworks for use later
        config = MailConfig(self.app)
        users = UsersBackend(self.app)
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        config.load()

        # Create a MySQL database for storing mailbox, alias and
        # domain information
        dbase.add('vmail', conn)
        passwd = hashlib.sha1(str(random.random())).hexdigest()[0:8]
        dbase.usermod('vmail', 'add', passwd, conn)
        dbase.chperm('vmail', 'vmail', 'grant', conn)

        # Add system user and group for handling mail
        users.add_sys_user('vmail')
        users.add_group('vmail')
        users.add_to_group('vmail', 'vmail')
        uid = users.get_user('vmail', users.get_all_users()).uid
        gid = users.get_group('vmail', users.get_all_groups()).gid
        pfgid = users.get_group('dovecot', users.get_all_groups()).gid

        # Create the virtual mail directory
        if not os.path.exists('/var/vmail'):
            os.mkdir('/var/vmail')
        users.change_user_param('vmail', 'home', '/var/vmail')
        users.change_user_param('vmail', 'shell', '/sbin/nologin')
        os.chmod('/var/vmail', 770)
        os.chown('/var/vmail', uid, gid)

        # Tell Dovecot (MDA) where to find users and passwords
        config.dovecot_authsql = {
            'passdb_0': {
                'driver': 'sql',
                'args': '/etc/dovecot/dovecot-sql.conf.ext'
            },
            'userdb_0': {
                'driver': 'sql',
                'args': '/etc/dovecot/dovecot-sql.conf.ext'
            }
        }

        # Tell Dovecot how to read our SQL
        config.dovecot_dovecotsql['driver'] = 'mysql'
        config.dovecot_dovecotsql['connect'] = \
            'host=localhost dbname=vmail user=vmail password=%s'%passwd
        config.dovecot_dovecotsql['default_pass_scheme'] = 'MD5-CRYPT'
        config.dovecot_dovecotsql['password_query'] = (
            'SELECT username as user, password, \'/var/vmail/%d/%n\''
            ' as userdb_home, \'maildir:/var/vmail/%d/%n\' as userdb_mail,'
            ' 150 as userdb_uid, 8 as userdb_gid FROM mailbox '
            'WHERE username = \'%u\' AND active = \'1\'')
        config.dovecot_dovecotsql['user_query'] = (
            'SELECT \'/var/vmail/%d/%n\' as home, '
            '\'maildir:/var/vmail/%d/%n\' as mail, 150 AS uid, 8 AS gid, '
            'concat(\'dirsize:storage=\', quota) AS quota FROM mailbox '
            'WHERE username = \'%u\' AND active = \'1\'')
        config.dovecot_auth['disable_plaintext_auth'] = 'yes'
        config.dovecot_auth['auth_mechanisms'] = 'plain login'
        for x in config.dovecot_auth:
            if x.startswith('include') and config.dovecot_auth[x] != 'auth-sql.conf.ext':
                del config.dovecot_auth[x]
        config.dovecot_auth['include_0'] = 'auth-sql.conf.ext'

        # Tell Dovecot where to put its mail and how to save/access it
        config.dovecot_mail['mail_location'] = 'maildir:/var/vmail/%d/%n'
        config.dovecot_mail['mail_uid'] = 'vmail'
        config.dovecot_mail['mail_gid'] = 'vmail'
        config.dovecot_mail['first_valid_uid'] = str(uid)
        config.dovecot_mail['last_valid_uid'] = str(uid)

        # Tell Dovecot to communicate with Postfix (MTA)
        config.dovecot_master['service auth_0'] = {
            'unix_listener auth-userdb_0': {
                'mode': '0600',
                'user': 'vmail',
                'group': 'vmail'
            },
            'unix_listener /var/spool/postfix/private/auth_0': {
                'mode': '0660',
                'user': 'postfix',
                'group': 'postfix'
            }
        }

        # Protect Dovecot configuration folder
        for r, d, f in os.walk('/etc/dovecot'):
            for x in d:
                os.chown(os.path.join(r, x), uid, pfgid)
                st = os.stat(os.path.join(r, x))
                os.chmod(os.path.join(r, x), st.st_mode&~stat.S_IROTH&~stat.S_IWOTH&~stat.S_IXOTH)
            for x in f:
                os.chown(os.path.join(r, x), uid, pfgid)
                st = os.stat(os.path.join(r, x))
                os.chmod(os.path.join(r, x), st.st_mode&~stat.S_IROTH&~stat.S_IWOTH&~stat.S_IXOTH)

        # Tell Postfix (MTA) how to get mailbox, alias and domain info
        # from our MySQL database
        f = open('/etc/postfix/mysql_virtual_alias_domainaliases_maps.cf', 'w')
        f.write('user = vmail\n'
            'password = '+passwd+'\n'
            'hosts = 127.0.0.1\n'
            'dbname = vmail\n'
            'query = SELECT goto FROM alias,alias_domain\n'
            '  WHERE alias_domain.alias_domain = \'%d\'\n'
            '  AND alias.address=concat(\'%u\', \'@\', alias_domain.target_domain)\n'
            '  AND alias.active = 1\n')
        f.close()
        f = open('/etc/postfix/mysql_virtual_alias_maps.cf', 'w')
        f.write('user = vmail\n'
            'password = '+passwd+'\n'
            'hosts = 127.0.0.1\n'
            'dbname = vmail\n'
            'table = alias\n'
            'select_field = goto\n'
            'where_field = address\n'
            'additional_conditions = and active = \'1\'\n')
        f.close()
        f = open('/etc/postfix/mysql_virtual_domains_maps.cf', 'w')
        f.write('user = vmail\n'
            'password = '+passwd+'\n'
            'hosts = 127.0.0.1\n'
            'dbname = vmail\n'
            'table = domain\n'
            'select_field = domain\n'
            'where_field = domain\n'
            'additional_conditions = and backupmx = \'0\' and active = \'1\'\n')
        f.close()
        f = open('/etc/postfix/mysql_virtual_mailbox_domainaliases_maps.cf', 'w')
        f.write('user = vmail\n'
            'password = '+passwd+'\n'
            'hosts = 127.0.0.1\n'
            'dbname = vmail\n'
            'query = SELECT maildir FROM mailbox, alias_domain\n'
            '  WHERE alias_domain.alias_domain = \'%d\'\n'
            '  AND mailbox.username=concat(\'%u\', \'@\', alias_domain.target_domain )\n'
            '  AND mailbox.active = 1\n')
        f.close()
        f = open('/etc/postfix/mysql_virtual_mailbox_maps.cf', 'w')
        f.write('user = vmail\n'
            'password = '+passwd+'\n'
            'hosts = 127.0.0.1\n'
            'dbname = vmail\n'
            'table = mailbox\n'
            'select_field = CONCAT(domain, \'/\', local_part)\n'
            'where_field = username\n'
            'additional_conditions = and active = \'1\'\n')
        f.close()
        f = open('/etc/postfix/header_checks', 'w')
        f.write('/^Received:/                 IGNORE\n'
            '/^User-Agent:/               IGNORE\n'
            '/^X-Mailer:/                 IGNORE\n'
            '/^X-Originating-IP:/         IGNORE\n'
            '/^x-cr-[a-z]*:/              IGNORE\n'
            '/^Thread-Index:/             IGNORE\n')
        f.close()

        # Configure Postfix
        config.postfix_main = {
            'smtpd_banner': '$myhostname ESMTP $mail_name',
            'biff': 'no',
            'append_dot_mydomain': 'no',
            'readme_directory': 'no',
            'smtpd_sasl_type': 'dovecot',
            'smtpd_sasl_path': 'private/auth',
            'smtpd_sasl_auth_enable': 'yes',
            'broken_sasl_auth_clients': 'yes',
            'smtpd_sasl_security_options': 'noanonymous',
            'smtpd_sasl_local_domain': '',
            'smtpd_sasl_authenticated_header': 'yes',
            'smtp_tls_note_starttls_offer': 'no',
            'smtpd_tls_loglevel': '1',
            'smtpd_tls_received_header': 'yes',
            'smtpd_tls_session_cache_timeout': '3600s',
            'tls_random_source': 'dev:/dev/urandom',
            'smtpd_use_tls': 'no',
            'smtpd_enforce_tls': 'no',
            'smtp_use_tls': 'no',
            'smtp_enforce_tls': 'no',
            'smtpd_tls_security_level': 'may',
            'smtp_tls_security_level': 'may',
            'unknown_local_recipient_reject_code': '450',
            'maximal_queue_lifetime': '7d',
            'minimal_backoff_time': '1800s',
            'maximal_backoff_time': '8000s',
            'smtp_helo_timeout': '60s',
            'smtpd_recipient_limit': '16',
            'smtpd_soft_error_limit': '3',
            'smtpd_hard_error_limit': '12',
            'smtpd_helo_restrictions': 'permit_mynetworks, warn_if_reject reject_non_fqdn_hostname, reject_invalid_hostname, permit',
            'smtpd_sender_restrictions': 'permit_sasl_authenticated, permit_mynetworks, warn_if_reject reject_non_fqdn_sender, reject_unknown_sender_domain, reject_unauth_pipelining, permit',
            'smtpd_client_restrictions': 'reject_rbl_client sbl.spamhaus.org, reject_rbl_client blackholes.easynet.nl',
            'smtpd_recipient_restrictions': 'reject_unauth_pipelining, permit_mynetworks, permit_sasl_authenticated, reject_non_fqdn_recipient, reject_unknown_recipient_domain, reject_unauth_destination, permit',
            'smtpd_data_restrictions': 'reject_unauth_pipelining',
            'smtpd_relay_restrictions': 'reject_unauth_pipelining, permit_mynetworks, permit_sasl_authenticated, reject_non_fqdn_recipient, reject_unknown_recipient_domain, reject_unauth_destination, permit',
            'smtpd_helo_required': 'yes',
            'smtpd_delay_reject': 'yes',
            'disable_vrfy_command': 'yes',
            'myhostname': self.app.get_backend(IHostnameManager).gethostname().lower(),
            'myorigin': '/etc/hostname',
            'mydestination': '',
            'mynetworks': '127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128',
            'mailbox_size_limit': '0',
            'recipient_delimiter': '+',
            'inet_interfaces': 'all',
            'mynetworks_style': 'host',
            'virtual_mailbox_base': '/var/vmail',
            'virtual_mailbox_maps': 'mysql:/etc/postfix/mysql_virtual_mailbox_maps.cf, mysql:/etc/postfix/mysql_virtual_mailbox_domainaliases_maps.cf',
            'virtual_uid_maps': 'static:'+str(uid),
            'virtual_gid_maps': 'static:'+str(gid),
            'virtual_alias_maps': 'mysql:/etc/postfix/mysql_virtual_alias_maps.cf, mysql:/etc/postfix/mysql_virtual_alias_domainaliases_maps.cf',
            'virtual_mailbox_domains': 'mysql:/etc/postfix/mysql_virtual_domains_maps.cf',
            'virtual_transport': 'dovecot',
            'dovecot_destination_recipient_limit': '1',
            'header_checks': 'regexp:/etc/postfix/header_checks',
            'enable_original_recipient': 'no'
        }
        config.postfix_master['smtp'] = ['inet', 'n', '-', '-', '-', '-', 'smtpd']
        config.postfix_master['smtps'] = ['inet', 'n', '-', '-', '-', '-', 'smtpd',
            'syslog_name=postfix/smtps', 'smtpd_tls_wrappermode=yes',
            'smtpd_sasl_auth_enable=yes', 'smtpd_tls_auth_only=yes',
            'smtpd_client_restrictions=permit_sasl_authenticated,reject_unauth_destination,reject',
            'smtpd_sasl_security_options=noanonymous,noplaintext',
            'smtpd_sasl_tls_security_options=noanonymous']
        config.postfix_master['dovecot'] = ['unix', '-', 'n', 'n', '-', '-', 'pipe',
            'flags=DRhu user=vmail:mail argv=/usr/lib/dovecot/dovecot-lda -d $(recipient)']

    def list_domains(self):
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        d = dbase.execute('vmail', 
            'SELECT domain FROM domain;', conn, False)
        for x in d:
            if x == ('ALL',):
                d.remove(x)
        return [x[0] for x in d]

    def list_mailboxes(self, domain):
        r = []
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        d = dbase.execute('vmail', 
            'SELECT local_part FROM mailbox WHERE domain = %s;'%domain, 
            conn, False)
        for x in d:
            r.append({'name': d[0], 'domain': domain})
        return r

    def list_aliases(self, domain):
        r = []
        dbase = apis.databases(self.app).get_interface('MariaDB')
        conn = apis.databases(self.app).get_dbconn('MariaDB')
        d = dbase.execute('vmail', 
            'SELECT address,goto FROM alias WHERE domain = %s;'%domain, 
            conn, False)
        for x in d:
            r.append({'name': d[0], 'forward': d[1], 'domain': domain})
        return r

    def add_mailbox(self, name, dom, passwd, quota=False):
        pass

    def del_mailbox(self, name, dom):
        pass

    def add_alias(self, name, dom, forward):
        pass

    def del_alias(self, name, dom, forward):
        pass

    def add_domain(self, name):
        pass

    def del_domain(self, name):
        pass

    def chpasswd(self, name, dom, passwd):
        pass


class MailSSLPlugin(Plugin):
    implements(ISSLPlugin)
    text = 'Mailserver'
    iconfont = 'gen-envelop'
    cert_type = 'cert-key'

    def enable_ssl(self, cert, key):
        config = MailConfig(self.app)
        config.load()
        config.postfix_main['smtpd_tls_cert_file'] = cert
        config.postfix_main['smtpd_tls_key_file'] = key
        config.postfix_main['smtpd_use_tls'] = 'yes'
        config.postfix_main['smtp_tls_note_starttls_offer'] = 'yes'
        config.postfix_main['smtp_tls_security_level'] = 'may'
        config.postfix_main['smtpd_tls_security_level'] = 'may'
        config.postfix_main['smtpd_tls_auth_only'] = 'yes'
        config.postfix_main['smtp_tls_ciphers'] = 'high'
        config.postfix_main['smtp_tls_exclude_ciphers'] = ['aNULL', 
            'DES', '3DES', 'MD5', 'DES+MD5', 'RC4']
        config.postfix_main['smtpd_tls_protocols'] = ['TLSv1.2',
            'TLSv1.1', 'TLSv1.0', 'SSLv3', '!SSLv2']
        config.dovecot_ssl['ssl'] = 'yes'
        config.dovecot_ssl['ssl_cert'] = '<'+cert
        config.dovecot_ssl['ssl_key'] = '<'+key
        config.save()

    def disable_ssl(self):
        config = MailConfig(self.app)
        config.load()
        del config.postfix_main['smtpd_tls_cert_file']
        del config.postfix_main['smtpd_tls_key_file']
        del config.postfix_main['smtpd_tls_auth_only']
        del config.postfix_main['smtp_tls_note_starttls_offer']
        del config.postfix_main['smtpd_use_tls']
        del config.postfix_main['smtp_tls_security_level']
        del config.postfix_main['smtpd_tls_security_level']
        del config.postfix_main['smtp_tls_ciphers']
        del config.postfix_main['smtp_tls_exclude_ciphers']
        del config.postfix_main['smtpd_tls_protocols']
        config.dovecot_ssl['ssl'] = 'no'
        config.dovecot_ssl['ssl_cert'] = ''
        config.dovecot_ssl['ssl_key'] = ''
        config.save()
