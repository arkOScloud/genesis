# Plugin metadata
NAME = 'Chat (XMPP)'
TYPE = 'plugin'
ICON = 'gen-bubbles'
DESCRIPTION = 'Host your own chat/IM server'
LONG_DESCRIPTION = ('XMPP (also known as Jabber) is an open protocol for '
    'real-time instant messaging and chat between different clients. '
    'This plugin hosts an XMPP server on your device, registers user '
    'accounts and intermediates communication between multiple services.')
CATEGORIES = [
    {
        "primary": "Communication",
        "secondary": ["Chat", "Instant Messaging (IM)"]
    }
]
VERSION = '0.1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "The Prosody Team"
APP_HOMEPAGE = "https://prosody.im"
LOGO = False

SERVICES = [
    {
        "name": "XMPP Chat Server",
        "binary": "prosody",
        "ports": [('tcp', '5222'), ('tcp', '5269')]
    }
]

# Plugin parameters
MODULES = ['main', 'backend']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Prosody",
            "package": "prosody",
            "binary": "prosodyctl"
        },
        {
            "type": "app",
            "name": "LUA",
            "package": "lua51",
            "binary": None
        },
        {
            "type": "app",
            "name": "LUA Security",
            "package": "lua51-sec",
            "binary": None
        }
    ]
}
GENERATION = 1
