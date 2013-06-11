MODULES = ['api', 'main', 'component', 'pm_apt', 'pm_pacman', 'pm_portage', 'pm_ports',  'pm_yum']

DEPS =  [
    (['debian'],
     [
        ('app', 'dpkg', 'dpkg')
     ]),
    (['arch', 'arkos'],
     [
        ('app', 'pacman', 'pacman')
     ]),
    (['centos', 'fedora'],
     [
        ('app', 'yum', 'yum')
    ]),
    (['freebsd'],
     [
        ('app', 'pkg-tools', 'portupgrade')
    ]),
    (['gentoo'],
     [
        ('app', 'eix', 'eix'),
     ]),
]

NAME = 'Package Manager'
ICON = 'gen-cube'
PLATFORMS = ['debian', 'arch', 'arkos', 'freebsd', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Install, update and remove applications on your system'
VERSION = '4'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
