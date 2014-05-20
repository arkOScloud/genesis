from genesis.com import *
from genesis.apis import API
from genesis.api import CategoryPlugin, event
from genesis import apis
from genesis.ui import UI
from base64 import b64encode, b64decode


class Dashboard (API):
    """
    Dashboard API
    """
    class IWidget(Interface):
        """
        Interface for a dashboard widget

        - ``iconfont`` - `str`, iconfont class
        - ``title`` - `str`, short title text
        - ``name`` - `str`, name shown in 'choose widget' dialog
        - ``style`` - `str`, 'normal' and 'linear' now supported
        """
        title = ''
        name = ''
        iconfont = ''
        style = 'normal'

        def get_ui(self, cfg, id=None):
            """
            Returns plugin UI (Layout or Element)

            :param  id:     plugin ID
            :type   id:     str
            :param  cfg:    saved plugin configuration
            :type   cfg:    str
            """

        def handle(self, event, params, cfg, vars=None):
            """
            Handles UI event of a plugin

            :param  cfg:    saved plugin configuration
            :type   cfg:    str
            """

        def get_config_dialog(self):
            """
            Returns configuration dialog UI (Layout or Element), or None
            """

        def process_config(self, vars):
            """
            Saves configuration from the configuration dialog (get_config_dialog)

            :rtype   cfg:    str
            """

    class WidgetManager (Plugin):
        def __init__(self):
            self.refresh()

        def refresh(self):
            self._left = []
            self._right = []
            self._widgets = {}

            try:
                self._left = [int(x) for x in self.app.config.get('dashboard', 'left').split(',')]
                self._right = [int(x) for x in self.app.config.get('dashboard', 'right').split(',')]
            except:
                pass

            for x in (self._left + self._right):
                self._widgets[x] = (
                    self.app.config.get('dashboard', '%i-class'%x),
                    eval(b64decode(self.app.config.get('dashboard', '%i-cfg'%x)))
                )

        def list_left(self): return self._left
        def list_right(self): return self._right

        def add_widget(self, id, cfg):
            if id.__class__ is not str:
                id = id.plugin_id
            idx = 0
            while idx in self._widgets:
                idx += 1
            self._widgets[idx] = (id, cfg)
            self._left.append(idx)
            self.save_cfg()

        def reorder(self, nl, nr):
            self._left = nl
            self._right = nr
            self.save_cfg()

        def remove_widget(self, id):
            if id in self._right:
                self._right.remove(id)
            else:
                self._left.remove(id)
            del self._widgets[id]
            self.app.config.remove_option('dashboard', '%i-class'%id)
            self.app.config.remove_option('dashboard', '%i-cfg'%id)
            self.save_cfg()

        def save_cfg(self):
            self.app.config.set('dashboard', 'left', ','.join(str(x) for x in self._left))
            self.app.config.set('dashboard', 'right', ','.join(str(x) for x in self._right))
            for x in self._widgets:
                self.app.config.set('dashboard', '%i-class'%x, self._widgets[x][0])
                self.app.config.set(
                    'dashboard', '%i-cfg'%x,
                    b64encode(repr(self._widgets[x][1]))
                )
            self.app.config.save()

        def get_widget_object(self, id):
            return self.get_by_name(self._widgets[id][0])

        def get_widget_config(self, id):
            return self._widgets[id][1]

        def get_by_name(self, id):
            try:
                return self.app.grab_plugins(
                   apis.dashboard.IWidget,
                   lambda x:x.plugin_id==id,
                )[0]
            except:
                return None


class SysStat(API):
    class ISysStat(Interface):
        def get_load(self):
            pass
        
        def get_ram(self):
            pass
            
        def get_swap(self):
            pass


class Services(API):
    class IServiceManager(Interface):
        def list_all(self):
            pass

        def get_status(self, name):
            pass

        def start(self, name):
            pass

        def stop(self, name):
            pass

        def restart(self, name):
            pass


    class Service:
        name = ''

        @property
        def status(self):
            if not hasattr(self, '_status'):
                self._status = self.mgr.get_status(self.name)
            return self._status

        @property
        def enabled(self):
            if not hasattr(self, '_enabled'):
                self._enabled = self.mgr.get_enabled(self.name)
            return self._enabled

        def __cmp__(self, b):
            return 1 if self.name > b.name else -1

        def __str__(self):
            return self.name
            
    
    class ServiceControlPlugin(CategoryPlugin):
        abstract = True
        display = False
        disports = False
        
        services = []
        
        def get_ui(self):
            from genesis.plugins.security.firewall import RuleManager, FWMonitor

            mgr = self.app.get_backend(apis.services.IServiceManager)
            rum = RuleManager(self.app)
            self._rules_list = rum.get_by_plugin(self.plugin_id)
            fwm = FWMonitor(self.app)

            res = UI.DT(UI.DTR(
                    UI.DTH(width=20),
                    UI.DTH(UI.Label(text='Service')),
                    UI.DTH(width=20),
                    header=True
                  ), width='100%', noborder=True)

            alert = False

            services = self.plugin_info.services if hasattr(self.plugin_info, 'services') else self.services
            for s in services:
                ctl = UI.HContainer()

                try:
                    st = mgr.get_status(s['binary'])
                except:
                    st = 'failed'
                    alert = True
                try:
                    en = mgr.get_enabled(s['binary'])
                except:
                    en = 'failed'

                if st == 'running':
                    ctl.append(UI.TipIcon(text='Stop', cls='servicecontrol', iconfont='gen-stop', id='stop/' + s['binary']))
                    ctl.append(UI.TipIcon(text='Restart', cls='servicecontrol', iconfont='gen-loop-2', id='restart/' + s['binary']))
                else:
                    ctl.append(UI.TipIcon(text='Start', cls='servicecontrol', iconfont='gen-play-2', id='start/' + s['binary']))
                    alert = True
                if en == 'enabled':
                    ctl.append(UI.TipIcon(text='Disable', cls='servicecontrol', iconfont='gen-minus-circle', id='disable/' + s['binary']))
                else:
                    ctl.append(UI.TipIcon(text='Enable', cls='servicecontrol', iconfont='gen-plus-circle', id='enable/' + s['binary']))
                
                t = UI.DTR(
                        UI.HContainer(
                            UI.IconFont(iconfont='gen-' + ('play-2' if st == 'running' else 'stop')),
                            UI.IconFont(iconfont='gen-' + ('checkmark' if en == 'enabled' else 'close-2')),
                        ),
                        UI.Label(text='%s (%s)'%(s['name'], s['binary'])),
                        ctl
                    )
                res.append(t)

            ptalert = False

            if self._rules_list != []:
                pts = UI.DT(UI.DTR(
                        UI.DTH(width=20),
                        UI.DTH(UI.Label(text='Application')),
                        UI.DTH(UI.Label(text='Ports')),
                        UI.DTH(UI.Label(text='Authorization')),
                        UI.DTH(width=20),
                        header=True
                      ), width='100%', noborder=True)
                for p in self._rules_list:
                    if p[1] == 1:
                        perm, ic, show = 'Local', 'gen-home', [2, 0]
                    elif p[1] == 2:
                        perm, ic, show = 'All', 'gen-earth', [1, 0]
                    else:
                        perm, ic, show = 'None', 'gen-close', [2, 1]
                        ptalert = True
                    pts.append(UI.DTR(
                        UI.IconFont(iconfont=p[0].icon),
                        UI.Label(text=p[0].name),
                        UI.Label(text=', '.join(str(x[1]) for x in p[0].ports)),
                        UI.HContainer(
                            UI.IconFont(iconfont=ic),
                            UI.Label(text=' '),
                            UI.Label(text=perm),
                            ),
                        UI.HContainer(
                            (UI.TipIcon(iconfont='gen-earth',
                                text='Allow All', cls='servicecontrol', 
                                id='2/' + str(self._rules_list.index(p))) if 2 in show else None),
                            (UI.TipIcon(iconfont='gen-home',
                                text='Local Only', cls='servicecontrol',
                                id='1/' + str(self._rules_list.index(p))) if 1 in show else None),
                            (UI.TipIcon(iconfont='gen-close', 
                                text='Deny All', cls='servicecontrol',
                                id='0/' + str(self._rules_list.index(p)),
                                warning='Are you sure you wish to deny all access to %s? '
                                'This will prevent anyone (including you) from connecting to it.' 
                                % p[0].name) if 0 in show else None),
                            ),
                       ))
            
            panel = UI.ServicePluginPanel(
                alert=('True' if alert else 'False'),
                ports=('True' if self._rules_list != [] else 'False'),
                ptalert=('True' if ptalert else 'False'),
            )

            if self.display:
                dlg = UI.DialogBox(
                        UI.ScrollContainer(res),
                        id='dlgServices',
                        hidecancel='True'
                    )
                return UI.Container(panel, dlg, self.get_main_ui())
            elif self.disports:
                dlg = UI.DialogBox(
                        UI.ScrollContainer(pts),
                        id='dlgPorts',
                        hidecancel='True'
                    )
                return UI.Container(panel, dlg, self.get_main_ui())
            else:
                return UI.Container(panel, self.get_main_ui())

        @event('servicecontrol/click')
        def on_service_control(self, event, params, vars=None):
            from genesis.plugins.security.firewall import RuleManager, FWMonitor
            if params[0] == 'services':
                self.display = True
            if params[0] == 'security':
                self.disports = True
            if params[0] == '2':
                RuleManager(self.app).set(self._rules_list[int(params[1])][0], 2)
                FWMonitor(self.app).regen()
            if params[0] == '1':
                RuleManager(self.app).set(self._rules_list[int(params[1])][0], 1)
                FWMonitor(self.app).regen()
            if params[0] == '0':
                sel = self._rules_list[int(params[1])][0]
                RuleManager(self.app).set(sel, 0)
                FWMonitor(self.app).regen()
            if params[0] == 'restart':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.restart(params[1])
            if params[0] == 'start':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.start(params[1])
            if params[0] == 'stop':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.stop(params[1])
            if params[0] == 'enable':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.enable(params[1])
            if params[0] == 'disable':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.disable(params[1])
