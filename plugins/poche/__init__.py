MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'mariadb', 'mysqld'),
    	('app', 'nginx', 'nginx'),
    	('app', 'php', 'php'),
    	('app', 'php-fpm', 'php-fpm'),
    	('app', 'php-xcache', 'php-xcache'),
    	('app', 'php-tidy', 'php-tidy'),
    	('plugin', 'db-mariadb')
     ])
]

NAME = 'Poche'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Self-hosted read-it-later app'
VERSION = '0'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
