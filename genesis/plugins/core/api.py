from genesis.com import *


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
