# Plugin metadata
NAME = 'Mailserver ALPHA'
TYPE = 'plugin'
ICON = 'gen-envelop'
DESCRIPTION = 'Host your email server and accounts'
LONG_DESCRIPTION = ''
CATEGORIES = [
    {
        "primary": "Communication",
        "secondary": ["Email"]
    }
]
VERSION = '0'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
LOGO = False

SERVICES = [
    {
        "name": "Mail Transport",
        "binary": "postfix",
        "ports": [('tcp', '25'), ('tcp', '587')]
    },
    {
        "name": "Mail Delivery",
        "binary": "dovecot",
        "ports": [('tcp', '143')]
    },
    {
        "name": "MariaDB",
        "binary": "mysqld",
        "ports": []
    }
]

# Plugin parameters
MODULES = ['main', 'backend', 'config']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Postfix",
            "package": "postfix",
            "binary": "postfix"
        },
        {
            "type": "app",
            "name": "Dovecot",
            "package": "dovecot",
            "binary": "dovecot"
        },
        {
            "type": "app",
            "name": "MariaDB",
            "package": "mariadb",
            "binary": "mysqld"
        },
        {
            "type": "plugin",
            "name": "MariaDB",
            "package": "db-mariadb"
        }
    ]
}
GENERATION = 1
