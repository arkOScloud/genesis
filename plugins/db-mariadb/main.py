from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import *


class MariaDB(Plugin):
    implements(apis.databases.IDatabase)
    name = 'MariaDB'
    icon = 'gen-database'
    multiuser = True

    def add(self, dbname):
        status = shell_cs(
            'mysql -e "CREATE DATABASE %s;"' % dbname, stderr=True
        )
        if status[0] >= 1:
            raise Exception(status[1])

    def remove(self, dbname):
        status = shell_cs(
            'mysql -e "DROP DATABASE %s;"' % dbname, stderr=True
        )
        if status[0] >= 1:
            raise Exception(status[1])

    def usermod(self, user, action, passwd):
        if action == 'add':
            status = shell_cs(
                'mysql -e "CREATE USER \'%s\'@\'localhost\' IDENTIFIED BY \'%s\';"'
                % (user,passwd), stderr=True
            )
        elif action == 'del':
            status = shell_cs(
                'mysql -e "DROP USER \'%s\'@\'localhost\';"'
                % user, stderr=True
            )
        if status[0] >= 1:
            raise Exception(status[1])

    def chperm(self, dbname, user, action):
        if action == 'check':
            status = shell_cs(
                'mysql -e "SHOW GRANTS FOR \'%s\@\'localhost\';"'
                % user, stderr=True
            )
        if action == 'grant':
            status = shell_cs(
                'mysql -e "GRANT ALL ON %s.* TO \'%s\'@\'localhost\';"' 
                % (dbname,user), stderr=True
            )
        elif action == 'revoke':
            status = shell_cs(
                'mysql -e "REVOKE ALL ON %s.* TO \'%s\'@\'localhost\';"' 
                % (dbname,user), stderr=True
            )
        if status[0] >= 1:
            raise Exception(status[1])

    def execute(self, dbname, command):
        return shell('mysql -e "%s" %s' % (command, dbname), stderr=True)

    def get_dbs(self):
        dblist = []
        excludes = ['Database', 'information_schema', 
            'mysql', 'performance_schema']
        dbs = shell('mysql -e "SHOW DATABASES;"')
        for line in dbs.split('\n'):
            if not line in excludes and line is not '':
                dblist.append({
                    'name': line,
                    'type': 'MariaDB',
                    'class': self.__class__
                })
        return dblist

    def get_users(self):
        userlist = []
        output = shell('mysql -e "SELECT user FROM mysql.user;"')
        for line in output:
            if not line in userlist:
                userlist.append({
                    'name': line,
                    'type': 'MariaDB'
                    'class': self.__class__
                })
        return userlist
