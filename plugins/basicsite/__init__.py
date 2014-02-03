# Plugin metadata
NAME = 'Basic Website'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Upload your own HTML/PHP files'
LONG_DESCRIPTION = 'Create a custom website with your own HTML or PHP files.'
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Websites", "Static Sites"]
    }
]
VERSION = '1'

AUTHOR = 'arkOS'
HOMEPAGE = 'https://arkos.io'
LOGO = False

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
WA_PLUGIN = 'Website'
DPATH = None
DBENGINE = None
PHP = False
NOMULTI = False
SSL = True
