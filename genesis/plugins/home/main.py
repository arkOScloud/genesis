from genesis.ui import *
from genesis import apis
from genesis import api

class HomePlugin(api.CategoryPlugin):
    text = 'My Apps'
    iconfont = 'gen-home'
    folder = 'top'

    folders = {
        'cluster': 'CLUSTER',
        'system': 'SYSTEM',
        'hardware': 'HARDWARE',
        'apps': 'APPLICATIONS',
        'servers': 'SERVERS',
        'advanced': 'ADVANCED',
        'other': 'OTHER',
    }

    folder_ids = ['cluster', 'apps', 'servers', 'system', 'hardware', 'advanced', 'other']

    def on_session_start(self):
        if self.app.gconfig.get('genesis', 'ssl') == '0':
            self.put_message('warn', 'Please enable SSL to ensure secure communication with the server')

    def on_init(self):
        pass

    def get_ui(self):   
        ui = self.app.inflate('home:home')
        cats = self.app.grab_plugins(api.ICategoryProvider)
        webs = self.app.grab_plugins(apis.webapps.IWebapp)
        btnlist = []

        for x in cats:
            if x.folder in self.folder_ids:
                btnlist.append({'id': x.plugin_id, 
                    'type': 'plugin',
                    'icon': x.plugin_info.iconfont if hasattr(x.plugin_info, 'iconfont') else x.iconfont,
                    'name': x.text})
        for x in webs:
            btnlist.append({'id': x.plugin_info.id,
                'type': 'webapp',
                'icon': x.plugin_info.iconfont,
                'name': x.plugin_info.name})
        
        for x in sorted(btnlist, key=lambda y: y['name']):
            ui.append('main', 
                UI.HomeButton(
                    id=x['id'],
                    type=x['type'],
                    iconfont=x['icon'],
                    name=x['name']
                    )
                )

        return ui
