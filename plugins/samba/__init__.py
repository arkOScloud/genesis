MODULES = ['backend', 'main']

DEPS =  [
    (['any'],
     [
    	('app', 'Samba', 'smbd'),
        ('plugin', 'services'),
     ])
]

NAME = 'Samba'
PLATFORMS = ['any']
DESCRIPTION = 'Control Samba server'
VERSION = '2'
GENERATION = 1
AUTHOR = 'Genesis team'
HOMEPAGE = 'http://genesis.org'
