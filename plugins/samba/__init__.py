# Plugin metadata
NAME = 'Fileshares (Windows)'
TYPE = 'plugin'
ICON = 'gen-upload-2'
DESCRIPTION = 'Add, remove and manage Samba (SMB/CIFS) shares'
CATEGORIES = [
    {
        "primary": "File Storage",
        "secondary": ["Documents", "Music", "Photos"]
    }
]
VERSION = '5'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "The Samba Team"
APP_HOMEPAGE = "https://www.samba.org/"

# Plugin parameters
MODULES = ["main", "backend"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Samba",
            "package": "samba",
            "binary": "smbd"
        }
    ]
}
GENERATION = 1
