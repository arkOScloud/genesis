MODULES = ['api', 'main', 'config']

DEPS =  [
    (['any'],
     [
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'Web Server'
PLATFORMS = ['debian', 'arch', 'arkos', 'freebsd', 'gentoo', 'centos', 'mandriva']
DESCRIPTION = 'Controls the nginx webserver'
VERSION = '3'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
