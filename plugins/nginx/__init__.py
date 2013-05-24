MODULES = ['api', 'main', 'config']

DEPS =  [
    (['any'],
     [
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'Web Server'
ICON = 'gen-earth'
PLATFORMS = ['debian', 'arch', 'arkos', 'freebsd', 'gentoo', 'centos', 'mandriva']
DESCRIPTION = 'Controls the nginx webserver'
VERSION = '4'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
