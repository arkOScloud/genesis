from genesis.api import *
from genesis.plugmgr import RepositoryManager
from genesis.utils import *

import time
import feedparser


class FeedUpdater (Component):
    name = 'updater'

    def on_starting(self):
        self.feed = {}

    def get_feed(self):
        return self.feed

    def run(self):
        rm = RepositoryManager(self.app.log, self.app.config)
        feed_url = feedparser.parse('http://arkos.io/feed')

        while True:
            try:
                self.feed = []
                rm.update_list(crit=True)
                for e in feed_url.entries:
                    self.feed.append({'title': e.title, 'link': e.link, 
                        'time': e.published_parsed})
            except:
                pass
            time.sleep(60*60*12) # check once every 12 hours


class UpdateCheck(Component):
    name = 'updcheck'

    def on_starting(self):
        self.update = False
        self.version = ''

    def get_status(self):
        return (self.update, self.version)

    def check_updates(self, refresh=False):
        if refresh:
            shell('pacman -Sy')
        out = shell('pacman -Qu')
        try:
            for thing in out.split('\n'):
                if not thing.strip():
                    continue
                if thing.split()[0] == 'genesis':
                    self.update = True
                    self.version = thing.split()[1]
        except Exception, e:
            self.app.log.error('Update check failed: ' + str(e))

    def run(self):
        try:
            status = self.app.gconfig.get('genesis', 'updcheck')
        except:
            status = '1'
        if status == '1':
            platform = detect_platform()
            if platform == 'arkos' or platform == 'arch':
                self.check_updates()
                time.sleep(60*60*24) # check once every day
