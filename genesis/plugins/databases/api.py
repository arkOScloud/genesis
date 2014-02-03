from genesis.com import *
from genesis import apis
from genesis.utils import shell_status

from utils import *

class Databases(apis.API):
    def __init__(self, app):
        self.app = app

    class IDatabase(Interface):
        def add(self):
            pass

        def remove(self):
            pass

        def usermod(self):
            pass

        def chperm(self):
            pass

        def execute(self):
            pass

        def get_dbs(self):
            pass

        def get_users(self):
            pass

    def get_dbconn(self, dbtype):
        if self.app.session.has_key('dbconns') and \
        dbtype in self.app.session['dbconns']:
            return self.app.session['dbconns'][dbtype]
        elif self.app.session.has_key('dbconns'):
            return False
        else:
            self.app.session['dbconns'] = {}
            return False

    def clear_dbconn(self, dbtype):
        if self.app.session.has_key('dbconns') and \
        dbtype in self.app.session['dbconns']:
            del self.app.session['dbconns'][dbtype]

    def get_dbtypes(self):
        dblist = []
        for plugin in self.app.grab_plugins(apis.databases.IDatabase):
            active = None
            if plugin.plugin_info.db_task:
                status = shell_status('systemctl is-active %s' % plugin.plugin_info.db_task)
                if status is 0:
                    active = True
                else:
                    active = False
            dblist.append((plugin.plugin_info.db_name, plugin.plugin_info.db_task, active))
        return dblist

    def get_databases(self):
        try:
            dblist = []
            for plugin in self.app.grab_plugins(apis.databases.IDatabase):
                if plugin.plugin_info.multiuser:
                    try:
                        dbconn = self.app.session['dbconns'][plugin.plugin_info.db_name]
                        for item in plugin.get_dbs(dbconn):
                            dblist.append(item)
                    except:
                        pass
                else:
                    for item in plugin.get_dbs():
                        dblist.append(item)
            return dblist
        except DBConnFail:
            return []

    def get_info(self, name):
        return filter(lambda x: x.__class__.__name__ == name,
            self.app.grab_plugins(apis.databases.IDatabase))[0].plugin_info

    def get_interface(self, name):
        return filter(lambda x: x.__class__.__name__ == name,
            self.app.grab_plugins(apis.databases.IDatabase))[0]

    def get_users(self):
        try:
            userlist = []
            for plugin in self.app.grab_plugins(apis.databases.IDatabase):
                if plugin.plugin_info.multiuser:
                    try:
                        dbconn = self.app.session['dbconns'][plugin.plugin_info.db_name]
                        for item in plugin.get_users(dbconn):
                            userlist.append(item)
                    except:
                        pass
            return userlist
        except DBConnFail:
            return []


