import ConfigParser
import glob
import os
import re

from genesis.com import *
from genesis.utils import *
from genesis import apis


class ArchServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['arch', 'arkos']

    def __init__(self):
        self.use_systemd = os.path.realpath("/proc/1/exe").endswith("/systemd")

    def list_all(self):
        services = {}

        if self.use_systemd:
            for x in glob.iglob('/usr/lib/systemd/system/*.service'):
                service = re.sub('\.service$', '', x.rsplit('/')[5])
                services[service] = {"running": None, "enabled": False}
            for x in glob.iglob('/etc/systemd/system/*.wants/*.service'):
                service = re.sub('\.service$', '', x.rsplit('/')[5])
                try:
                    services[service]["enabled"] = True
                except:
                    pass
            for unit in shell("systemctl --no-ask-password --full -t service --all").splitlines():
                data = unit.split()
                if data == [] or not data[0].endswith('.service'):
                    continue
                service = re.sub('\.service$', '', data[0])
                try:
                    services[service]["running"] = data[2]=="active"
                except:
                    pass
        else:
            services = os.listdir('/etc/rc.d')

        r = []
        for s in services:
            svc = apis.services.Service()
            svc.stype = 'system'
            svc.name = s
            svc._status = services[s]["running"]
            svc._enabled = services[s]["enabled"]
            svc.mgr = self
            r.append(svc)

        if not os.path.exists('/etc/supervisor.d'):
            os.mkdir('/etc/supervisor.d')
        for x in os.listdir('/etc/supervisor.d'):
            x = x.split('.ini')[0]
            svc = apis.services.Service()
            svc.stype = 'supervisor'
            svc.name = x
            svc._status = self.get_status(x, 'supervisor') if self.get_status('supervisord') == 'running' else 'unknown'
            svc._enabled = self.get_enabled(x, 'supervisor')
            svc.mgr = self
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name, stype='system'):
        if stype == 'supervisor':
            status = shell("supervisorctl status {}".format(name))
            return 'running' if 'RUNNING' in status else 'stopped'
        elif self.use_systemd:
            status = shell_status("systemctl --no-ask-password is-active {}.service".format(name))
            return 'stopped' if status != 0 else 'running'
        else:
            s = shell('/etc/rc.d/{} status'.format(name))
            return 'running' if 'running' in s else 'stopped'

    def get_enabled(self, name, stype='system'):
        if stype == 'supervisor':
            return 'enabled' if os.path.exists(os.path.join('/etc/supervisor.d', name+'.ini')) else 'disabled'
        elif self.use_systemd:
            status = shell_status("systemctl --no-ask-password is-enabled {}.service".format(name))
            return 'disabled' if status != 0 else 'enabled'
        else:
            return 'unknown'

    def get_log(self, name, stype='system'):
        if stype == 'supervisor':
            s = shell("supervisorctl tail {}".format(name), stderr=True)
        elif self.use_systemd:
            s = shell("systemctl --no-ask-password status {}.service".format(name), stderr=True)
        else:
            s = shell('/etc/rc.d/{} status'.format(name), stderr=True)
        return s

    def start(self, name, stype='system'):
        if stype == 'supervisor':
            shell("supervisorctl start {}".format(name))
        elif self.use_systemd:
            shell("systemctl --no-ask-password start {}.service".format(name))
        else:
            shell('/etc/rc.d/{} start'.format(name))

    def stop(self, name, stype='system'):
        if stype == 'supervisor':
            shell("supervisorctl stop {}".format(name))
        elif self.use_systemd:
            shell("systemctl --no-ask-password stop {}.service".format(name))
        else:
            shell('/etc/rc.d/{} stop'.format(name))

    def restart(self, name, stype='system'):
        if stype == 'supervisor':
            shell("supervisorctl restart {}".format(name))
        elif self.use_systemd:
            shell("systemctl --no-ask-password reload-or-restart {}.service".format(name))
        else:
            shell('/etc/rc.d/{} restart'.format(name))

    def real_restart(self, name, stype='system'):
        if stype == 'supervisor':
            shell("supervisorctl restart {}".format(name))
        elif self.use_systemd:
            shell("systemctl --no-ask-password restart {}.service".format(name))
        else:
            shell('/etc/rc.d/{} restart'.format(name))

    def enable(self, name, stype='system'):
        if stype == 'supervisor':
            if os.path.exists(os.path.join('/etc/supervisor.d', name+'.ini.disabled')):
                os.rename(os.path.join('/etc/supervisor.d', name+'.ini.disabled'),
                    os.path.join('/etc/supervisor.d', name+'.ini'))
            if not self.get_status("supervisord") == "running":
                self.start("supervisord")
            shell("supervisorctl reload")
            shell("supervisorctl start {}".format(name))
        elif self.use_systemd:
            shell("systemctl --no-ask-password enable {}.service".format(name))

    def disable(self, name, stype='system'):
        if stype == 'supervisor':
            shell("supervisorctl stop {}".format(name))
            shell("supervisorctl remove {}".format(name))
            os.rename(os.path.join('/etc/supervisor.d', name+'.ini'),
                os.path.join('/etc/supervisor.d', name+'.ini.disabled'))
        elif self.use_systemd:
            shell("systemctl --no-ask-password disable {}.service".format(name))

    def edit(self, name, opts, start=True, stype='supervisor'):
        if stype == 'supervisor':
            title = '%s:%s' % (opts['stype'], name)
            c = ConfigParser.RawConfigParser()
            c.add_section(title)
            for x in opts:
                if x != 'stype':
                    c.set(title, x, opts[x])
            c.write(open(os.path.join('/etc/supervisor.d', name+'.ini'), 'w'))

    def delete(self, name, stype='supervisor'):
        if stype == 'supervisor':
            shell("supervisorctl stop {}".format(name))
            shell("supervisorctl remove {}".format(name))
            try:
                os.unlink(os.path.join('/etc/supervisor.d', name+'.ini'))
                os.unlink(os.path.join('/etc/supervisor.d', name+'.ini.disabled'))
            except:
                pass
