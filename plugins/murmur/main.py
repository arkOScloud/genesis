from genesis.ui import *
from genesis.api import *
from genesis import apis

class MurmurPlugin(apis.services.ServiceControlPlugin):
    text = 'Mumble Server'
    iconfont = 'gen-bubbles'
    folder = 'servers'