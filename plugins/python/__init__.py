# Plugin metadata
NAME = 'Python'
TYPE = 'plugin'
ICON = 'gen-code'
DESCRIPTION = 'Extension functions for Python applications and websites'
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
            "name": "Python 2.x",
            "package": "python2",
            "binary": "python2"
        },
        {
            "type": "module",
            "name": "gunicorn",
            "package": "gunicorn",
            "binary": "gunicorn"
        },
        {
            "type": "module",
            "name": "django",
            "package": "django",
            "binary": "django"
        }
    ]
}
GENERATION = 1
