MODULES = ['main', 'backend']

DEPS = [(['any'],
         [
             ('app', 'transmission-cli', 'transmission-daemon'),
             ('plugin')
             ]
        )]

NAME = 'Transmission (Bittorrent client)'
ICON = 'gen-download'
PLATFORMS = ['any']
DESCRIPTION = 'Manage Transmission headless Bittorrent client'
VERSION = '0'
GENERATION = 1
AUTHOR = 'will'
HOMEPAGE = 'http://arkos.io'