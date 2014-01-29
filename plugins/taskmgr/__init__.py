# Plugin metadata
NAME = 'Task Manager'
TYPE = 'plugin'
ICON = 'gen-enter'
DESCRIPTION = 'View and/or kill running processes'
CATEGORIES = [
    {
        "primary": "Utilities",
        "secondary": []
    }
]
VERSION = '3'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'

# Plugin parameters
MODULES = ["main"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "module",
            "name": "Python psutil",
            "package": "psutil",
            "binary": "psutil"
        }
    ]
}
GENERATION = 1
