from genesis.ui import *
from genesis.com import implements, Plugin
from genesis.api import *
from genesis import apis
from updater import Updater

# We want apis.dashboard already!
import genesis.plugins.sysmon.api


class NewsWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Project news'
    icon = '/dl/core/ui/stock/news.png'
    name = 'Project news'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        ui = self.app.inflate('core:news')
        feed = Updater.get().get_feed()
        if feed is not '':
            for i in feed:
                ui.append('list', UI.CustomHTML(html='<a href="%s" target="_blank"><li>%s</li></a>'%(feed[i],i)))
        return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, event, params, vars):
        pass
