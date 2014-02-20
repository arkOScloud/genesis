# -*- coding: UTF-8 -*-
# Plugin metadata
NAME = 'Wallabag'
TYPE = 'webapp'
ICON = 'gen-feed'
DESCRIPTION = 'Self-hosted app for saving web pages and RSS feeds'
LONG_DESCRIPTION = ('Wallabag (formerly poche) is a self-hostable application '
    'for saving web pages. Unlike other services, wallabag is free '
    '(as in freedom) and open-source.')
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["News Readers (RSS)"]
    }
]
VERSION = '1.5.0-3'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Nicholas Lœuillet"
APP_HOMEPAGE = "http://www.wallabag.org/"
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
MODULES = ["main"]
PLATFORMS = ["any"]
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
            "type": "app",
            "name": "PHP Tidy",
            "package": "php-tidy",
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
WA_PLUGIN = 'Wallabag'
DPATH = 'https://github.com/wallabag/wallabag/archive/1.5.0.tar.gz'
DBENGINE = 'MariaDB'
PHP = True
NOMULTI = True
SSL = True
