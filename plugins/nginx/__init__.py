MODULES = ['main', 'main_single', 'config']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'Web Server (nginx)'
PLATFORMS = ['debian', 'arch', 'arkos', 'freebsd', 'gentoo', 'centos', 'mandriva']
DESCRIPTION = 'Controls the nginx webserver'
VERSION = '2'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
