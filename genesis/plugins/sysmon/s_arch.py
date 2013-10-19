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
        services = []

        if self.use_systemd:
            for unit in shell("systemctl --no-ask-password --full -t service --all").splitlines():
                data = unit.split()
                if data == [] or not data[0].endswith('.service'):
                    continue
                if 'inactive' in data[2]:
                    status = 'stopped'
                else:
                    status = 'running'
                services.append((re.sub('\.service$', '', data[0]), status))
        else:
            services = os.listdir('/etc/rc.d')

        r = []
        for s in services:
            svc = apis.services.Service()
            svc.name = s[0]
            svc._status = s[1]
            svc.mgr = self
            r.append(svc)

        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        if self.use_systemd:
            status = shell_status("systemctl --no-ask-password is-active {}.service".format(name))

            if status != 0:
                return 'stopped'
            else:
                return 'running'
        else:
            s = shell('/etc/rc.d/{} status'.format(name))
            return 'running' if 'running' in s else 'stopped'

    def start(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password start {}.service".format(name))
        else:
            shell('/etc/rc.d/{} start'.format(name))

    def stop(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password stop {}.service".format(name))
        else:
            shell('/etc/rc.d/{} stop'.format(name))

    def restart(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password reload-or-restart {}.service".format(name))
        else:
            shell('/etc/rc.d/{} restart'.format(name))

    def real_restart(self, name):
        if self.use_systemd:
            shell("systemctl --no-ask-password restart {}.service".format(name))
        else:
            shell('/etc/rc.d/{} restart'.format(name))
