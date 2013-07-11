MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'MariaDB', 'mysqld'),
    	('app', 'nginx', 'nginx'),
    	('app', 'PHP', 'php'),
    	('app', 'PHP-FPM', 'php-fpm'),
    	('app', 'PHP-GD', 'php-gd'),
    	('app', 'PHP-Intl', 'php-intl'),
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
