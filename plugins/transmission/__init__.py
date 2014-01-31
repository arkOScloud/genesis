# Plugin metadata
NAME = 'Transmission'
TYPE = 'plugin'
ICON = 'gen-download'
DESCRIPTION = 'Manage Transmission headless Bittorrent client'
CATEGORIES = [
    {
        "primary": "Downloads",
        "secondary": ["Torrents"]
    }
]
VERSION = '1'

AUTHOR = 'will'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Transmission Project"
APP_HOMEPAGE = "http://www.transmissionbt.com/"

SERVICES = [
    {
        "name": "Transmission Client",
        "binary": "transmission",
        "ports": [('tcp', '9091')]
    }
]

# Plugin parameters
MODULES = ["main", "backend"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Transmission (CLI)",
            "package": "transmission-cli",
            "binary": "transmission"
        }
    ]
}
GENERATION = 1
