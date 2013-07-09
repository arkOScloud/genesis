MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'MariaDB', 'mysqld'),
    	('plugin', 'db-mariadb')
     ])
]

NAME = 'WordPress'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Host a blog with WordPress CMS'
VERSION = '0'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
