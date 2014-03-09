# Plugin metadata
NAME = 'ownCloud'
TYPE = 'webapp'
ICON = 'gen-cloud'
DESCRIPTION = 'Host calendar, files, contacts, and sync across devices'
LONG_DESCRIPTION = ('ownCloud gives you universal access to your files '
    'through a web interface or WebDAV. It also provides a '
    'platform to easily view & sync your contacts, '
    'calendars and bookmarks across all your devices and '
    'enables basic editing right on the web. Installation '
    'has minimal server requirements, doesn\'t need special '
    'permissions and is quick. ownCloud is extendable via a '
    'simple but powerful API for applications and plugins.')
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
VERSION = '6.0.2-1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "ownCloud"
APP_HOMEPAGE = "https://www.owncloud.org"
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
WA_PLUGIN = 'ownCloud'
DPATH = 'https://download.owncloud.org/community/owncloud-6.0.2.tar.bz2'
DBENGINE = 'MariaDB'
PHP = True
NOMULTI = True
SSL = True
