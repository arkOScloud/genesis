MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('app', 'iptables', 'iptables')
     ])
]

NAME = 'Firewall (iptables)'
ICON = 'gen-fire'
PLATFORMS = ['debian', 'arch', 'arkos', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Rules creation/management for the iptables Firewall'
VERSION = '3'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
