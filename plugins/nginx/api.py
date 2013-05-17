from genesis.com import *
from genesis.apis import API
from genesis.api import CategoryPlugin, event
from genesis.ui import UI
from genesis import apis


class Webserver(API):
    
    class VirtualHost:
        def __init__(self):
            self.name = ''
            self.config = ''            


    class Module:
        def __init__(self):
            self.name = ''
            self.config = ''          
            self.has_config = False
              
                                
    class WebserverPlugin(apis.services.ServiceControlPlugin):
        abstract = True
        
        ws_service = 'none'
        ws_title = 'none'
        ws_backend = None
        ws_vhosts = True
        
        def on_init(self):
            self.service_name = self.ws_service
            self.tab_hosts = 0
            self._backend = self.ws_backend(self.app)
            
        def on_session_start(self):
            self._tab = 0
            self._creating_host = False
            self._editing_host = None
            
        def get_config(self):
            return self.app.get_config(self._backend)
            
        def get_main_ui(self):
            ui = self.app.inflate('nginx:main')
            tc = UI.TabControl(active=self._tab)
            if self.ws_vhosts:
                tc.add('Hosts', self.get_ui_hosts(ui))
            else:
                ui.remove('addhost')
            ui.append('main', tc)
            return ui
            
        def get_ui_hosts(self, gui):
            ui = self.app.inflate('nginx:hosts')
            tbl = ui.find('list') 
               
            hosts = self._backend.get_hosts()
            for x in sorted(hosts.keys()):
                tbl.append(UI.DTR(
                            UI.Image(file='/dl/core/ui/stock/status-%sabled.png'%(
                                'en' if hosts[x].enabled else 'dis')),
                            UI.Label(text=x),
                            UI.DTD(
                                UI.HContainer(
                                    UI.TipIcon(
                                        icon='/dl/core/ui/stock/edit.png',
                                        id='edithost/'+x, 
                                        text='Edit'
                                    ),
                                    UI.TipIcon(
                                        icon='/dl/core/ui/stock/'+ ('dis' if hosts[x].enabled else 'en') + 'able.png',
                                        id='togglehost/'+x, 
                                        text='Disable' if hosts[x].enabled else 'Enable'
                                    ),
                                    UI.TipIcon(
                                        icon='/dl/core/ui/stock/delete.png',
                                        id='deletehost/'+x, 
                                        text='Delete',
                                        warning='Delete host %s'%x
                                    ),
                                    spacing=0
                                ),
                                hidden=True
                            )
                          ))
                            
            if self._creating_host:
                gui.append(
                    'main',
                    UI.InputBox(
                        text='Host config name', 
                        id='dlgCreateHost'
                    )
                )

            if self._editing_host is not None:
                gui.append(
                    'main',
                    UI.InputBox(
                        extra='code',
                        text='Host config', 
                        value=self._backend.get_hosts()[self._editing_host].config,
                        id='dlgEditHost'
                    )
                )
                
            return ui
                
        @event('button/click')
        def on_click(self, event, params, vars=None):
            if params[0] == 'togglehost':
                self._tab = self.tab_hosts
                h = self._backend.get_hosts()[params[1]]
                if h.enabled:
                    self._backend.disable_host(params[1])
                else:
                    self._backend.enable_host(params[1])
            if params[0] == 'deletehost':
                self._tab = self.tab_hosts
                self._backend.delete_host(params[1])
            if params[0] == 'edithost':
                self._tab = self.tab_hosts
                self._editing_host = params[1]
            if params[0] == 'addhost':
                self._tab = self.tab_hosts
                self._creating_host = True

        @event('dialog/submit')
        def on_submit(self, event, params, vars):
            if params[0] == 'dlgCreateHost':
                if vars.getvalue('action', '') == 'OK':
                    h = apis.webserver.VirtualHost()
                    h.name = vars.getvalue('value', '')
                    h.config = self._backend.host_template % h.name
                    self._backend.save_host(h)
                self._creating_host = False
            if params[0] == 'dlgEditHost':
                if vars.getvalue('action', '') == 'OK':
                    h = self._backend.get_hosts()[self._editing_host]
                    h.config = vars.getvalue('value', '')
                    self._backend.save_host(h)
                self._editing_host = None
