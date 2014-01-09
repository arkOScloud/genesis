MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'mariadb', 'mysqld'),
    	('module', '_mysql', 'mysql-python')
     ])
]

NAME = 'Database - MariaDB'
ICON = 'gen-database'
PLATFORMS = ['any']
DESCRIPTION = 'Add MariaDB support to Databases'
VERSION = '2'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'https://arkos.io'
