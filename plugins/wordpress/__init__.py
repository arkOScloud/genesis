# Plugin metadata
NAME = 'WordPress'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Open-source CMS and blogging platform'
LONG_DESCRIPTION = ('WordPress started as just a blogging system, '
    'but has evolved to be used as full content management system '
    'and so much more through the thousands of plugins, widgets, '
    'and themes, WordPress is limited only by your imagination. '
    '(And tech chops.)')
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Blogs", "Websites", "CMS"]
    }
]
VERSION = '3.8.1-1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Automattic"
APP_HOMEPAGE = "https://wordpress.org"
LOGO = True

SERVICES = [
    {
        "name": "MariaDB",
        "binary": "mysqld",
        "ports": []
    },
    {
        "name": "PHP FastCGI",
        "binary": "php-fpm",
        "ports": []
    }
]

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
        },
        {
            "type": "plugin",
            "name": "PHP",
            "package": "php"
        }
    ]
}
GENERATION = 1

# Webapp metadata
WA_PLUGIN = 'WordPress'
DPATH = 'https://wordpress.org/wordpress-3.8.1.tar.gz'
DBENGINE = 'MariaDB'
PHP = True
NOMULTI = True
SSL = True
