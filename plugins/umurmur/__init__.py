# Plugin metadata
NAME = 'Mumble Server'
TYPE = 'plugin'
ICON = 'gen-phone'
DESCRIPTION = 'Host your own Mumble server'
LONG_DESCRIPTION = ('uMurmur is the server application for Mumble, an open '
                    'source Voice-over-IP (VoIP) client. This plugin hosts the '
                    'umurmur server and lets you manage it.')
CATEGORIES = [
    {
        "primary": "Communication",
        "secondary": ["VoIP", "Voice-over-IP"]
    }
]
VERSION = '1'

AUTHOR = 'Heiner'
HOMEPAGE = 'http://github.com/heinzK1X'
APP_AUTHOR = "The Mumble Community"
APP_HOMEPAGE = "http://mumble.sourceforge.net"
LOGO = True

SERVICES = [
    {
        "name": "Mumble VoIP Server",
        "binary": "umurmur",
        "ports": [('tcp', '64738'), ('udp', '64738')]
    }
]

# Plugin parameters
MODULES = ['main', 'backend']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "uMurmur",
            "package": "umurmur",
            "binary": "umurmurd"
        },
        {
            "type": "module",
            "name": "pyparsing",
            "package": "pyparsing"
        },
        {
            "type": "module",
            "name": "pylibconfig2",
            "package": "pylibconfig2"
        }
    ]
}
GENERATION = 1
