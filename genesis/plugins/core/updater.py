from genesis.api import *
from genesis.plugmgr import RepositoryManager
from genesis.utils import *

import time
import json

FEED_URL = 'http://search.twitter.com/search.json?callback=?&rpp=5&q=from:genesis'


class Updater (Component):
    name = 'updater'

    def on_starting(self):
        self.feed = None

    def get_feed(self): return self.feed

    def run(self):
        rm = RepositoryManager(self.app.config)

        while True:
            try:
                rm.update_list()
                self.feed = json.loads(download(FEED_URL))['results']
            except:
                pass
            time.sleep(60*60*12) # each 12 hrs
