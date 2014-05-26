from genesis.api import *
from genesis.ui import *
from genesis import apis

class HomePlugin(CategoryPlugin):
    text = 'Home'
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
        cats = self.app.grab_plugins(ICategoryProvider)
        cats = sorted(cats, key=lambda p: p.text)

        for fld in self.folder_ids:
            for x in cats:
                if x.folder == fld:
                    ui.append('main', 
                        UI.HomeButton(
                            id=x.plugin_id,
                            iconfont=x.plugin_info.iconfont if hasattr(x.plugin_info, 'iconfont') else x.iconfont,
                            name=x.text
                            )
                        )

        return ui
