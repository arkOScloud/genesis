from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import *


class MariaDB(Plugin):
    implements(apis.databases.IDatabase)
    name = 'MariaDB'
    icon = 'gen-database'

    def add(self, dbname):
        shell('mysql -e "CREATE DATABASE %s;"' % dbname)

    def remove(self, dbname):
        shell('mysql -e "DROP DATABASE %s;"' % dbname)

    def adduser(self):
        pass

    def deluser(self):
        pass

    def get_dbs(self):
        dblist = []
        excludes = ['Database', 'information_schema', 'mysql', 'performance_schema']
        dbs = shell('mysql -e "SHOW DATABASES;"')
        for line in dbs.split('\n'):
            if not line in excludes and line is not '':
                dblist.append({'name': line, 'type': 'MariaDB', 'class': self.__class__})
        return dblist
