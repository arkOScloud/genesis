MODULES = ['main']

DEPS =  [
    (['any'],
     [
        ('app', 'nodejs', 'nodejs'),
        ('app', 'nginx', 'nginx'),
        ('app', 'sqlite', 'sqlite'),
        ('app', 'python2', 'python2'),
        ('plugin', 'db-sqlite3')
     ])
]

NAME = 'Ghost'
ICON = 'gen-earth'
PLATFORMS = ['any']
DESCRIPTION = 'Host a blog with Ghost'
VERSION = '1'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
