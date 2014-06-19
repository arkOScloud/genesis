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

    def validate(self, name='', user='', passwd='', conn=None):
        pass

    def add(self, dbname, conn=None):
        if re.search('\.|-|`|\\\\|\/|[ ]', dbname):
            raise Exception('Name must not contain spaces, dots, dashes or other special characters')
        self.chkpath()
        path = '/var/lib/sqlite3/%s.db' % dbname
        status = shell_cs('sqlite3 %s "ATTACH \'%s\' AS %s;"' % (path,path,dbname), stderr=True)
        if status[0] >= 1:
            raise Exception(status[1])

    def remove(self, dbname, conn=None):
        shell('rm /var/lib/sqlite3/%s.db' % dbname)

    def usermod(self, user, action, passwd, conn=None):
        pass

    def chperm(self, dbname, user, action, conn=None):
        pass

    def execute(self, dbname, command, conn=None, strf=False):
        cmds = command.split(';')
        conn = sqlite3.connect('/var/lib/sqlite3/%s.db' % dbname)
        c = conn.cursor()
        out = []
        for x in cmds:
            if x.split():
                c.execute('%s' % x)
                out += c.fetchall()
        conn.commit()
        if not strf:
            return out
        else:
            status = ''
            for line in out:
                status += line + '\n'
            return status

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

    def get_size(self, dbname, conn=None):
        return str_fsize(os.path.getsize(os.path.join('/var/lib/sqlite3', dbname+'.db')))

    def dump(self, dbname, conn=None):
        self.chkpath()
        conn = sqlite3.connect('/var/lib/sqlite3/%s.db' % dbname)
        data = ""
        for x in conn.iterdump():
            data += x
        return data
