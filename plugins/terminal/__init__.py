# Plugin metadata
NAME = 'Terminal'
TYPE = 'plugin'
ICON = 'gen-console'
DESCRIPTION = 'Remote VT100 command line from your browser window'
CATEGORIES = [
    {
        "primary": "Utilities",
        "secondary": ["Advanced", "Command line (CLI)"]
    }
]
VERSION = '3'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'

# Plugin parameters
MODULES = ["main", "config"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "module",
            "name": "Python PILlow",
            "package": "pillow",
            "binary": "PIL"
        }
    ]
}
GENERATION = 1
