MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('app', 'iptables', 'iptables')
     ])
]

NAME = 'Firewall (iptables)'
PLATFORMS = ['debian', 'arch', 'arkos', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Rules creation/management for the iptables Firewall'
VERSION = '2'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
