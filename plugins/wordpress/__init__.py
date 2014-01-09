MODULES = ['main']

DEPS =  [
    (['any'],
     [
    	('app', 'mariadb', 'mysqld'),
    	('app', 'nginx', 'nginx'),
    	('app', 'php', 'php'),
    	('app', 'php-fpm', 'php-fpm'),
    	('app', 'php-xcache', 'php-xcache'),
    	('plugin', 'db-mariadb')
     ])
]

NAME = 'WordPress'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Host a blog with WordPress CMS'
VERSION = '3.8-1'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'https://arkos.io'
