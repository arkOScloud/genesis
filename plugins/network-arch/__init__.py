MODULES = [
    'api',
    'main',
    'nc_arch',
    'nc_bsd',
    'nc_debian',
    'nc_centos',
    'ncs_bsd_basic',
    'ncs_bsd_ipv4',
    'ncs_linux_basic',
    'ncs_linux_bootp',
    'ncs_linux_dhcp',
    'ncs_linux_ifupdown',
    'ncs_linux_ipv4',
    'ncs_linux_ppp',
    'nctp_bsd',
    'nctp_linux',
    'recovery',
    'widget'
]

DEPS =  ['netctl']

NAME = 'Network Connections'
PLATFORMS = ['arch']
DESCRIPTION = 'Manage ethernet/wireless connections and interfaces (arkOS)'
VERSION = '3'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
