# Plugin metadata
NAME = 'Supervisor'
TYPE = 'plugin'
ICON = 'gen-bullhorn'
DESCRIPTION = 'Control processes under supervisord'
CATEGORIES = [
    {
        "primary": "Management",
        "secondary": []
    }
]
VERSION = '0'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Supervisor"
APP_HOMEPAGE = "http://supervisord.org/"
LOGO = False

SERVICES = [
    {
        "name": "Supervisor",
        "binary": "supervisord",
        "ports": [('tcp', '9001')]
    }
]

# Plugin parameters
MODULES = ["main", "widget"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Supervisor",
            "package": "supervisord",
            "binary": "supervisorctl"
        }
    ]
}
GENERATION = 1

