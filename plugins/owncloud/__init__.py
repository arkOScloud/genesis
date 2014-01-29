# Plugin metadata
NAME = 'ownCloud'
TYPE = 'webapp'
ICON = 'gen-cloud'
DESCRIPTION = 'Host calendar, files, contacts, and sync across devices'
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Personal Cloud"]
    },
    {
        "primary": "File Storage",
        "secondary": ["Documents", "Music", "Photos", "Calendar", 
            "Contacts"]
    }
]
VERSION = '6.0.0a-1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "ownCloud"
APP_HOMEPAGE = "https://www.owncloud.org"

# Plugin parameters
MODULES = ['main']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "MariaDB",
            "package": "mariadb",
            "binary": "mysqld"
        },
        {
            "type": "app",
            "name": "nginx",
            "package": "nginx",
            "binary": "nginx"
        },
        {
            "type": "app",
            "name": "php",
            "package": "php",
            "binary": None
        },
        {
            "type": "app",
            "name": "PHP FastCGI",
            "package": "php-fpm",
            "binary": "php-fpm"
        },
        {
            "type": "app",
            "name": "PHP GD Image Processing",
            "package": "php-gd",
            "binary": None
        },
        {
            "type": "app",
            "name": "PHP Internationalization",
            "package": "php-intl",
            "binary": None
        },
        {
            "type": "app",
            "name": "PHP xCache",
            "package": "php-xcache",
            "binary": None
        },
        {
            "type": "plugin",
            "name": "MariaDB",
            "package": "db-mariadb"
        }
    ]
}
GENERATION = 1
