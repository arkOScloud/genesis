MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'MariaDB', 'mysqld'),
    	('plugin', 'db-mariadb')
     ])
]

NAME = 'ownCloud'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Host calendar, files, contacts, and sync across devices'
VERSION = '0'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
