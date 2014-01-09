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
        ('app', 'php-xcache', 'php-xcache'),
    	('plugin', 'db-mariadb')
     ])
]

NAME = 'ownCloud'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Host calendar, files, contacts, and sync across devices'
VERSION = '6.0.0a-1'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'https://arkos.io'
