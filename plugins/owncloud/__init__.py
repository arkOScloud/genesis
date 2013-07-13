MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'mariadb', 'mysqld'),
    	('app', 'nginx', 'nginx'),
    	('app', 'php', 'php'),
    	('app', 'php-fpm', 'php-fpm'),
    	('app', 'php-gd', 'php-gd'),
    	('app', 'php-intl', 'php-intl'),
        ('app', 'php-apc', 'php-apc'),
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
