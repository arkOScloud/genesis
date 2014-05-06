# Plugin metadata
NAME = 'Etherpad'
TYPE = 'webapp'
ICON = 'gen-pen'
DESCRIPTION = 'Collaborative Text Editing'
LONG_DESCRIPTION = ('Etherpad allows you to edit documents collaboratively in '
                    'real-time, much like a live multi-player editor that runs '
                    'in your browser. Write articles, press releases, to-do '
                    'lists, etc. together with your friends, fellow students '
                    'or colleagues, all working on the same document at the '
                    'same time.')
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Personal Cloud"]
    }
]
VERSION = '1.4.0-rc1'

AUTHOR = 'Heiner'
HOMEPAGE = 'http://github.com/heinzK1X'
APP_AUTHOR = "The Etherpad Foundation"
APP_HOMEPAGE = "http://etherpad.org/"
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
WA_PLUGIN = 'Etherpad'
DPATH = 'https://github.com/ether/etherpad-lite/tarball/1.4.0-rc1'
DBENGINE = None
PHP = False
NOMULTI = True
SSL = True

