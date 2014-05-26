# Plugin metadata
NAME = 'NodeJS'
TYPE = 'extension'
ICON = 'gen-code'
DESCRIPTION = 'Extension functions for NodeJS applications and websites'
CATEGORIES = [
    {
        "primary": "Management",
        "secondary": []
    }
]
VERSION = '0.3'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
LOGO = False

SERVICES = []

# Plugin parameters
MODULES = ["main"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "NodeJS",
            "package": "nodejs",
            "binary": "npm"
        }
    ]
}
GENERATION = 1
