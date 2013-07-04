from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import *

import os


class SQLite3(Plugin):
    implements(apis.databases.IDatabase)
    name = 'SQLite3'
    icon = 'gen-database'
    multiuser = False

    def add(self, dbname):
        path = '/var/lib/sqlite3/%s.db' % dbname
        status = shell_cs('sqlite3 %s "ATTACH \'%s\' AS %s;"' % (path,path,dbname), stderr=True)
        if status[0] >= 1:
            raise Exception(status[1])

    def remove(self, dbname):
        shell('rm /var/lib/sqlite3/%s.db' % dbname)

    def usermod(self):
        pass

    def chperm(self):
        pass

    def execute(self, dbname, command):
        return shell('sqlite3 /var/lib/sqlite3/%s.db "%s"' % (dbname, command), stderr=True)

    def get_dbs(self):
        dblist = []
        for thing in os.listdir('/var/lib/sqlite3'):
            if thing.endswith('.db'):
                dblist.append({'name': thing.rstrip('.db'), 'type': 'SQLite3', 'class': self.__class__})
        return dblist

    def get_users(self):
        pass
