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
        status = shell_cs('mysql -e "CREATE DATABASE %s;"' % dbname, stderr=True)
        if status[0] >= 1:
            raise Exception(status[1])

    def remove(self, dbname):
        status = shell_cs('mysql -e "DROP DATABASE %s;"' % dbname, stderr=True)
        if status[0] >= 1:
            raise Exception(status[1])

    def adduser(self):
        pass

    def deluser(self):
        pass

    def execute(self, dbname, command):
        return shell('mysql -e "%s" %s' % (command, dbname), stderr=True)

    def get_dbs(self):
        dblist = []
        excludes = ['Database', 'information_schema', 'mysql', 'performance_schema']
        dbs = shell('mysql -e "SHOW DATABASES;"')
        for line in dbs.split('\n'):
            if not line in excludes and line is not '':
                dblist.append({'name': line, 'type': 'MariaDB', 'class': self.__class__})
        return dblist
