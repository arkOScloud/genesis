# Plugin metadata
NAME = 'NodeJS'
TYPE = 'plugin'
ICON = 'gen-code'
DESCRIPTION = 'Extension functions for NodeJS applications and websites'
CATEGORIES = [
    {
        "primary": "Management",
        "secondary": []
    }
]
VERSION = '0.2'

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
        },
        {
            "type": "plugin",
            "name": "Supervisor",
            "package": "supervisor"
        }
    ]
}
GENERATION = 1
