from genesis.com import *
from genesis import apis


class IProgressBoxProvider(Interface):
    """
    Allows your plugin to show a background progress dialog 

    - ``iconfont`` - `str`, iconfont class
    - ``title`` - `str`, text describing current activity
    """
    iconfont = ""
    title = ""
    
    def has_progress(self):
        """
        :returns:       whether this plugin has any currently running activity
        """
        return False
        
    def get_progress(self):
        """
        :returns:       text describing activity's current status
        """
        return ''
        
    def can_abort(self):
        """
        :returns:       whether currently running activity can be aborted
        """
        return False
        
    def abort(self):
        """
        Should abort current activity
        """


class ISSLPlugin(Interface):
    text = ''
    iconfont = ''
    cert_type = 'cert-key'

    def enable_ssl(self):
        pass

    def disable_ssl(self):
        pass


class LangAssist(apis.API):
    def __init__(self, app):
        self.app = app

    class ILangMgr(Interface):
        name = ''

    def get_interface(self, name):
        return filter(lambda x: x.name == name,
            self.app.grab_plugins(apis.langassist.ILangMgr))[0]


class Orders(apis.API):
    def __init__(self, app):
        self.app = app

    class IListener(Interface):
        id = ''

        def order(self, *params):
            pass

    def get_interface(self, name):
        return filter(lambda x: x.id == name,
            self.app.grab_plugins(apis.orders.IListener))
