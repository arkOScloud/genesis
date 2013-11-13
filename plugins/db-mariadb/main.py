from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import *


class MariaDB(Plugin):
    implements(apis.databases.IDatabase)
    name = 'MariaDB'
    icon = 'gen-database'
    task = 'mysqld'
    multiuser = True

    def add(self, dbname):
        if ' ' in dbname or '-' in dbname:
            raise Exception('Database name must not contain spaces or dashes')
        elif len(dbname) > 16:
            raise Exception('Database name must be shorter than 16 characters')
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
            out = shell_cs(
                'mysql -e "SHOW GRANTS FOR \'%s\'@\'localhost\';"'
                % user, stderr=True
            )
            parse = []
            status = ''
            for line in out[1].split('\n'):
                if line.startswith('Grants for'):
                    continue
                elif line is '' or line is ' ':
                    continue
                else:
                    parse.append(line.split(' IDENT')[0])
            for line in parse:
                status += line + '\n'
            return status
        elif action == 'grant':
            status = shell_cs(
                'mysql -e "GRANT ALL ON %s.* TO \'%s\'@\'localhost\';"' 
                % (dbname,user), stderr=True
            )
        elif action == 'revoke':
            status = shell_cs(
                'mysql -e "REVOKE ALL ON %s.* FROM \'%s\'@\'localhost\';"' 
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
            if not line in excludes and line.split():
                dblist.append({
                    'name': line,
                    'type': 'MariaDB',
                    'class': self.__class__
                })
        return dblist

    def get_users(self):
        userlist = []
        excludes = ['root', ' ', '']
        output = shell('mysql -e "SELECT user FROM mysql.user;"')
        for line in output.split('\n')[1:]:
            if not line in userlist and not line in excludes:
                userlist.append({
                    'name': line,
                    'type': 'MariaDB',
                    'class': self.__class__
                })
        return userlist
