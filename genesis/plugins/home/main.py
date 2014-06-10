from genesis.ui import *
from genesis import apis
from genesis import api

from genesis.plugins.core.updater import UpdateCheck

class HomePlugin(api.CategoryPlugin):
    text = 'My Applications'
    iconfont = 'fa fa-home'
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
            self.put_message('warn', 'HTTPS is not enabled; you should enable it to help secure communication with arkOS. Go to Tools > Certificates to do so.')

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
                    'icon': x.plugin_info.icon if hasattr(x.plugin_info, 'icon') else x.iconfont,
                    'name': x.text})
        for x in webs:
            btnlist.append({'id': x.plugin_info.id,
                'type': 'webapp',
                'icon': x.plugin_info.icon,
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

        if UpdateCheck.get().get_status()[0] == True:
            self.put_message('info', 'An update for Genesis is available. See the Settings pane for details.')

        return ui
