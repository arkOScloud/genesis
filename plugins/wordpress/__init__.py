# Plugin metadata
NAME = 'WordPress'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Host a blog with WordPress CMS'
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Blogs", "Websites", "CMS"]
    }
]
VERSION = '3.8-1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Automattic"
APP_HOMEPAGE = "https://wordpress.org"

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
