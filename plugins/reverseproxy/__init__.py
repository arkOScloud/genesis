# Plugin metadata
NAME = 'Reverse Proxy'
TYPE = 'webapp'
ICON = 'gen-globe'
DESCRIPTION = 'Set up reverse proxies for custom applications'
LONG_DESCRIPTION = ''
CATEGORIES = [
    {
        "primary": "Development",
        "secondary": []
    }
]
VERSION = '0'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
LOGO = False

SERVICES = []

# Plugin parameters
MODULES = ['main']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "nginx",
            "package": "nginx",
            "binary": "nginx"
        }
    ]
}
GENERATION = 1

# Webapp metadata
WA_PLUGIN = 'ReverseProxy'
DPATH = ''
DBENGINE = ''
PHP = False
NOMULTI = False
SSL = True
