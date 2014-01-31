from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import *

import os
import re
import sqlite3


class SQLite3(Plugin):
    implements(apis.databases.IDatabase)

    def add(self, dbname):
        if re.search('\.|-|`|\\\\|\/|[ ]', dbname):
            raise Exception('Name must not contain spaces, dots, dashes or other special characters')
        self.chkpath()
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
        try:
            cmds = command.split(';')
            conn = sqlite3.connect('/var/lib/sqlite3/%s.db' % dbname)
            c = conn.cursor()
            parse = []
            for x in cmds:
                if x.split():
                    c.execute('%s' % x)
                    out = c.fetchall()
                    for line in out:
                        parse.append(line[0])
            status = ''
            for line in parse:
                status += line + '\n'
            return status
        except Exception, e:
            raise Exception('', e)

    def get_dbs(self):
        self.chkpath()
        dblist = []
        for thing in os.listdir('/var/lib/sqlite3'):
            if thing.endswith('.db'):
                dblist.append({'name': thing.split('.db')[0], 'type': 'SQLite3', 'class': self.__class__})
        return dblist

    def get_users(self):
        pass

    def chkpath(self):
        if not os.path.isdir('/var/lib/sqlite3'):
            os.makedirs('/var/lib/sqlite3')
