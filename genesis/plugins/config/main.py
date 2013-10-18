from genesis.api import *
from genesis.ui import *
from genesis.utils import hashpw
from genesis.plugins.recovery.api import *
from genesis.plugins.core.updater import UpdateCheck


class ConfigPlugin(CategoryPlugin):
    text = 'Settings'
    iconfont = 'gen-cog'
    folder = False

    def on_session_start(self):
        self._config = None
        self._restart = False
        self._updstat = (False, '')
        self._update = None

    def get_ui(self):
        ui = self.app.inflate('config:main')

        # General
        ui.find('bind_host').set('value', self.app.gconfig.get('genesis', 'bind_host', ''))
        ui.find('bind_port').set('value', self.app.gconfig.get('genesis', 'bind_port', ''))
        ui.find('ssl').set('text', ('Enabled' if self.app.gconfig.get('genesis', 'ssl', '')=='1' else 'Disabled'))
        ui.find('nofx').set('checked', self.app.gconfig.get('genesis', 'nofx', '')=='1')
        ui.find('updcheck').set('checked', self.app.gconfig.get('genesis', 'updcheck', '')=='1')
        ui.find('purge').set('checked', self.app.gconfig.get('genesis', 'purge', '')=='1')

        # Security
        ui.find('httpauth').set('checked', self.app.gconfig.get('genesis','auth_enabled')=='1')

        # Configs
        cfgs = self.app.grab_plugins(IModuleConfig)
        cfgs = sorted(cfgs, key=lambda config: config.target.__name__ if not hasattr(config.target, 'text') else config.target.text)
        t = ui.find('configs')
        for c in cfgs:
            if c.target:
                t.append(UI.DTR(
                UI.IconFont(iconfont=(None if not hasattr(c.target, 'iconfont') else c.target.iconfont)),
                UI.Label(text=(c.target.__name__ if not hasattr(c.target, 'text') else c.target.text)),
                UI.TipIcon(text='Edit', iconfont="gen-pencil-2", id='editconfig/'+c.target.__name__),
            ))

        # Updates
        self._updstat = UpdateCheck.get().get_status()
        if self._updstat[0] == True:
            ui.find('updstatus').set('text', 'An update for Genesis is available.')
            ui.find('updstatus').set('size', '3')
            ui.find('updaction').set('text', 'Update Now')
            ui.find('updaction').set('iconfont', 'gen-arrow-down-3')
            ui.find('updaction').set('design', 'primary')

        if self._config:
            ui.append('main',
                self.app.get_config_by_classname(self._config).get_ui_edit()
            )

        if self._update is not None:
            pass
        else:
            ui.remove('dlgUpdate')

        if self._changed:
            self.put_message('warn', 'Restart required')

        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'updaction':
            if self._updstat[0] == False:
                UpdateCheck.get().check_updates(refresh=True)
            else:
                self._update = True
        if params[0] == 'editconfig':
            self._config = params[1]
        if params[0] == 'restart':
            self.app.restart()
        if params[0] == 'shutdown':
            shell('shutdown -P now')
        if params[0] == 'reboot':
            shell('reboot')

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmGeneral':
            if vars.getvalue('action', '') == 'OK':
                if self.app.gconfig.get('genesis', 'bind_host', '') != vars.getvalue('bind_host', ''):
                    self._changed = True
                if self.app.gconfig.get('genesis', 'bind_port', '') != vars.getvalue('bind_port', ''):
                    self._changed = True
                if self.app.gconfig.get('genesis', 'ssl', '') != vars.getvalue('ssl', ''):
                    self._changed = True
                self.app.gconfig.set('genesis', 'bind_host', vars.getvalue('bind_host', ''))
                self.app.gconfig.set('genesis', 'bind_port', vars.getvalue('bind_port', '8000'))
                self.app.gconfig.set('genesis', 'ssl', vars.getvalue('ssl', '0'))
                self.app.gconfig.set('genesis', 'auth_enabled', vars.getvalue('httpauth', '0'))
                self.app.gconfig.set('genesis', 'nofx', vars.getvalue('nofx', '0'))
                self.app.gconfig.set('genesis', 'updcheck', vars.getvalue('updcheck', '1'))
                self.app.gconfig.set('genesis', 'purge', vars.getvalue('purge', '0'))
                self.app.gconfig.save()
                self.put_message('info', 'Settings saved.')
        if params[0] == 'dlgEditModuleConfig':
            if vars.getvalue('action','') == 'OK':
                cfg = self.app.get_config_by_classname(self._config)
                cfg.apply_vars(vars)
                cfg.save()
            self._config = None
        if params[0] == 'dlgUpdate':
            if vars.getvalue('action', '') == 'OK':
                shell('pacman -S --noconfirm genesis')
                self.put_message('err', 'Update complete. Please reboot your system.')
            self._update = None


class GenesisConfig (Plugin):
    implements (IConfigurable)
    name = 'Genesis'
    iconfont = 'gen-arkos-round'
    id = 'genesis'

    def list_files(self):
        return ['/etc/genesis/*']
