# Plugin metadata
NAME = 'Calendar/Contacts'
TYPE = 'plugin'
ICON = 'gen-calendar'
DESCRIPTION = 'Host your own CalDAV and CardDAV calendar/contacts sync server'
CATEGORIES = [
    {
        "primary": "File Storage",
        "secondary": ["Calendar", "Contacts"]
    }
]
VERSION = '0.1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = 'Radicale'
APP_HOMEPAGE = 'http://radicale.org'
LOGO = False

SERVICES = [
    {
        "name": "Calendar/Contacts Server",
        "binary": None,
        "ports": [('tcp', '5232')]
    }
]

# Plugin parameters
MODULES = ["main", "backend"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Python 2.x",
            "package": "python2",
            "binary": "python2"
        },
        {
            "type": "app",
            "name": "uWSGI",
            "package": "uwsgi",
            "binary": "uwsgi"
        },
        {
            "type": "app",
            "name": "uWSGI Common Plugin",
            "package": "uwsgi-plugin-common",
            "binary": None
        },
        {
            "type": "app",
            "name": "uWSGI Python2 Plugin",
            "package": "uwsgi-plugin-python2",
            "binary": None
        },
        {
            "type": "module",
            "name": "Radicale",
            "package": "radicale",
            "binary": "radicale"
        },
        {
            "type": "plugin",
            "name": "Python",
            "package": "python"
        },
        {
            "type": "plugin",
            "name": "Reverse Proxy",
            "package": "reverseproxy"
        },
        {
            "type": "plugin",
            "name": "Supervisor",
            "package": "supervisor"
        }
    ]
}
GENERATION = 1
