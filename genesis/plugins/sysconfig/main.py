from genesis.api import *
from genesis.ui import *
from genesis.utils import hashpw
from genesis.plugins.recovery.api import *
from genesis.plugins.core.updater import UpdateCheck
from genesis import apis
from genesis.utils import shell_cs
from genesis.plugins.network import backend

import os
import re

import zonelist


class SysConfigPlugin(CategoryPlugin):
    text = 'System Settings'
    iconfont = 'gen-cog'
    folder = False

    def on_init(self):
        self._mgr = self.app.get_backend(apis.services.IServiceManager)
        self._be = backend.Config(self.app)
        self.hostname = self._be.gethostname()

    def get_ui(self):
        ui = self.app.inflate('sysconfig:main')

        # General
        ui.find('hostname').set('value', self.hostname)
        if os.path.exists('/etc/localtime'):
            tz_active = os.path.realpath('/etc/localtime').split('/usr/share/zoneinfo/')[1]
        tz_sel = [UI.SelectOption(text=x, value=x, 
            selected=True if tz_active in x else False)
            for x in zonelist.zones]
        ui.appendAll('zoneselect', *tz_sel)

        # Tools
        if shell_cs('which logrunnerd')[0] != 0:
            lrstat = 'Not installed'
        else:
            if self._mgr.get_status('logrunner') == 'running':
                lrstat = 'Running'
                ui.find('fllogrunner').append(UI.Button(text="Stop", id="svc/logrunner/stop"))
            else:
                lrstat = 'Not running'
                ui.find('fllogrunner').append(UI.Button(text="Start", id="svc/logrunner/start"))
            if self._mgr.get_enabled('logrunner') == 'enabled':
                lrstat += ' and enabled on boot'
                ui.find('fllogrunner').append(UI.Button(text="Disable on boot", id="svc/logrunner/disable"))
            else:
                lrstat += ' and not enabled on boot'
                ui.find('fllogrunner').append(UI.Button(text="Enable on boot", id="svc/logrunner/enable"))
        if shell_cs('which beacond')[0] != 0:
            bestat = 'Not installed'
        else:
            if self._mgr.get_status('beacon') == 'running':
                lrstat = 'Running'
                ui.find('flbeacon').append(UI.Button(text="Stop", id="svc/beacon/stop"))
            else:
                lrstat = 'Not running'
                ui.find('flbeacon').append(UI.Button(text="Start", id="svc/beacon/start"))
            if self._mgr.get_enabled('beacon') == 'enabled':
                lrstat += ' and enabled on boot'
                ui.find('flbeacon').append(UI.Button(text="Disable on boot", id="svc/beacon/disable"))
            else:
                lrstat += ' and not enabled on boot'
                ui.find('flbeacon').append(UI.Button(text="Enable on boot", id="svc/beacon/enable"))
        ui.find('logrunner').set('text', lrstat)
        ui.find('beacon').set('text', bestat)

        if self._changed:
            self.put_message('warn', 'A restart is required for this setting change to take effect.')

        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'svc':
            if params[2] == 'start':
                self._mgr.start(params[1])
            elif params[2] == 'stop':
                self._mgr.stop(params[1])
            elif params[2] == 'enable':
                self._mgr.enable(params[1])
            elif params[2] == 'disable':
                self._mgr.disable(params[1])

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmGeneral':
            if vars.getvalue('action', '') == 'OK':
                hn = vars.getvalue('hostname', '')
                zone = vars.getvalue('zoneselect', 'UTC')
                if not hn:
                    self.put_message('err', 'Hostname must not be empty')
                elif not re.search('^[a-zA-Z0-9.-]', hn) or re.search('(^-.*|.*-$)', hn):
                    self.put_message('err', 'Hostname must only contain '
                        'letters, numbers, hyphens or periods, and must '
                        'not start or end with a hyphen.')
                else:
                    self._be.sethostname(vars.getvalue('hostname'))
                zone = zone.split('/')
                if len(zone) > 1:
                    zonepath = os.path.join('/usr/share/zoneinfo', zone[0], zone[1])
                else:
                    zonepath = os.path.join('/usr/share/zoneinfo', zone[0])
                if os.path.exists('/etc/localtime'):
                    os.remove('/etc/localtime')
                os.symlink(zonepath, '/etc/localtime')
                self.put_message('info', 'Settings saved.')
