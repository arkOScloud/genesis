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

        - ``icon`` - `str`, icon URI
        - ``title`` - `str`, short title text
        - ``name`` - `str`, name shown in 'choose widget' dialog
        - ``style`` - `str`, 'normal' and 'linear' now supported
        """
        title = ''
        name = ''
        icon = ''
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

        def __cmp__(self, b):
            return 1 if self.name > b.name else -1

        def __str__(self):
            return self.name
            
    
    class ServiceControlPlugin(CategoryPlugin):
        abstract = True
        
        service_name = 'none'
        service_expected_status = None
        
        def get_ui(self):
            mgr = self.app.get_backend(apis.services.IServiceManager)
            
            st = 'failed'
            st = mgr.get_status(self.service_name)
            try:
                st = mgr.get_status(self.service_name)
                if self.service_expected_status:        
                    if self.service_expected_status != st:
                        st = 'failed'
            except:
                st = 'failed'

            self.service_status = st
            self.service_expected_status = None
            
            panel = UI.ServicePluginPanel(
                status=self.service_status, 
                servicename=self.service_name
            )
            return UI.Container(panel, self.get_main_ui())

        @event('servicecontrol/click')
        def on_service_control(self, event, params, vars=None):
            if params[0] == 'restart':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.restart(self.service_name)
                self.service_expected_status = 'running'
            if params[0] == 'start':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.start(self.service_name)
                self.service_expected_status = 'running'
            if params[0] == 'stop':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.stop(self.service_name)
                self.service_expected_status = 'stopped'

