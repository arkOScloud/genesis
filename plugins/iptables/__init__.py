MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('app', 'iptables', 'iptables')
     ])
]

NAME = 'IP tables'
PLATFORMS = ['debian', 'arch', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Netfilter rules control plugin'
VERSION = '1'
GENERATION = 1
AUTHOR = 'Genesis team'
HOMEPAGE = 'http://genesis.org'
