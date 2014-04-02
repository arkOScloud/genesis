# Plugin metadata
NAME = 'Ghost'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Host a blog with Ghost'
LONG_DESCRIPTION = ('Ghost is a platform dedicated to one thing: Publishing. '
	'It\'s beautifully designed, completely customisable and completely Open '
	'Source. Ghost allows you to write and publish your own blog, giving you '
	'the tools to make it easy and even fun to do.')
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Blogs", "Websites", "CMS"]
    }
]
VERSION = '0.4.2-1'

AUTHOR = 'ajvb'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Ghost"
APP_HOMEPAGE = "https://ghost.org"
LOGO = True

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
        },
        {
            "type": "plugin",
            "name": "NodeJS",
            "package": "nodejs"
        }
    ]
}
GENERATION = 1

# Webapp metadata
WA_PLUGIN = 'Ghost'
DPATH = 'https://github.com/TryGhost/Ghost/releases/download/0.4.2/Ghost-0.4.2.zip'
DBENGINE = ''
PHP = False
NOMULTI = True
SSL = True
