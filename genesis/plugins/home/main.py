from genesis.api import *
from genesis.ui import *
from genesis import apis

class HomePlugin(CategoryPlugin):
    text = 'Home'
    iconfont = 'gen-home'
    folder = 'top'

    def on_init(self):
    	pass

    def get_ui(self):
    	if self.app.gconfig.get('genesis', 'ssl') == '0':
    	    self.put_message('warn', 'Please enable SSL to ensure secure communication with the server')
        return None
