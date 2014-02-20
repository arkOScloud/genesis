# Plugin metadata
NAME = 'Ruby'
TYPE = 'plugin'
ICON = 'gen-code'
DESCRIPTION = 'Extension functions for Ruby websites and applications'
CATEGORIES = [
    {
        "primary": "Management",
        "secondary": []
    }
]
VERSION = '0'

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
            "name": "ruby",
            "package": "ruby",
            "binary": "ruby"
        }
    ]
}
GENERATION = 1
