from genesis.ui import *
from genesis.com import implements, Plugin
from genesis.api import *
from genesis import apis

# We want apis.dashboard already!
import genesis.plugins.sysmon.api


class NewsWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Project news'
    icon = '/dl/core/ui/stock/news.png'
    name = 'Project news'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        pass

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, event, params, vars):
        pass
