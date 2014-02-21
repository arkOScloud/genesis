import ConfigParser
import os

from genesis import apis
from genesis.com import Plugin
from genesis.utils import shell, shell_status


class SVClient(Plugin):
    def test(self):
        mgr = self.app.get_backend(apis.services.IServiceManager)
        return mgr.get_status('supervisord') == 'running'

    def run(self, cmd):
        return shell('supervisorctl ' + cmd)

    def status(self):
        r = {}
        if self.test():
            for l in self.run('status').splitlines():
                l = l.split(None, 2)
                r[l[0]] = {
                    'status': '' if len(l)<2 else l[1],
                    'info': '' if len(l)<3 else l[2]
                }
        return r

    def list(self):
        r = []
        s = self.status()
        for x in os.listdir('/etc/supervisor.d'):
            x = x.split('.ini')[0]
            r.append({
                'name': x,
                'ptype': self.get_type(x),
                'status': s[x]['status'] if s else 'Unknown',
                'info': s[x]['info'] if s else 'Unknown'
            })
        return r

    def start(self, id):
        self.run('start ' + id)

    def restart(self, id):
        self.run('restart ' + id)

    def stop(self, id):
        self.run('stop ' + id)

    def tail(self, id):
        return self.run('tail ' + id)

    def get(self, id):
        d = []
        if os.path.exists(os.path.join('/etc/supervisor.d', id+'.ini')):
            c = ConfigParser.RawConfigParser()
            c.read(os.path.join('/etc/supervisor.d', id+'.ini'))
            for x in c.items(c.sections()[0]):
                d.append(x)
        return d

    def get_type(self, id):
        c = ConfigParser.RawConfigParser()
        c.read(os.path.join('/etc/supervisor.d', id+'.ini'))
        return c.sections()[0].split(':')[0]

    def set(self, ptype, id, cfg, restart=True):
        name = '%s:%s'%(ptype,id)
        c = ConfigParser.RawConfigParser()
        c.add_section(name)
        for x in cfg:
            c.set(name, x[0], x[1])
        c.write(open(os.path.join('/etc/supervisor.d', id+'.ini'), 'w'))
        if restart:
            self.run('reread')

    def remove(self, id, restart=False):
        self.stop(id)
        if os.path.exists(os.path.join('/etc/supervisor.d', id+'.ini')):
            os.unlink(os.path.join('/etc/supervisor.d', id+'.ini'))
        if restart:
            self.run('reread')
