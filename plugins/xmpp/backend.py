import os
import re
import urllib

from genesis.api import *
from genesis.com import *
from genesis import apis
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
        conf = ''
        for x in sorted(data):
            if type(data[x]) == str:
                conf += '%s = "%s"\n' % (x, data[x])
            if type(data[x]) == bool:
                conf += '%s = %s\n' % (x, 'true' if data[x] else 'false')
            elif type(data[x]) == dict and x.startswith('_'):
                conf += '%s "%s"\n' % (x.split('_')[1], x.split('_')[2])
                for y in data[x]:
                    if type(data[x][y]) == dict:
                        conf += '\t%s = {\n' % y
                        for z in data[x][y]:
                            conf += '\t\t%s = "%s";\n' % (z, data[x][y][z])
                        conf += '\t}\n'
                    elif type(data[x][y]) == bool:
                        conf += '\t%s = %s\n' % (y, 'true' if data[x][y] else 'false')
                    else:
                        conf += '\t%s = "%s";\n' % (y, data[x][y])
                conf += '\n'
            elif type(data[x]) == dict:
                if not data[x]:
                    conf += '%s = { }\n\n' % x
                else:
                    conf += '%s = {\n' % x
                for y in data[x]:
                    if type(y) == int:
                        conf += '\t"%s";\n' % data[x][y]
                    elif type(data[x][y]) == bool:
                        conf += '\t%s = %s\n' % (y, 'true' if data[x][y] else 'false')
                    else:
                        conf += '\t%s = "%s";\n' % (y, data[x][y])
                if data[x]:
                    conf += '}\n\n'
        return conf


class XMPPUserControl:
    def list_users(self):
        users = []
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


#class GeneralConfig(ModuleConfig):
#    target=XMPPConfig
#    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']
#
#    labels = {
#        'cfg_file': 'Configuration file'
#    }
#
#    cfg_file = '/etc/prosody/prosody.cfg.lua'
