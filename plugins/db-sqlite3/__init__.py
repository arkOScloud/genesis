# Plugin metadata
NAME = 'Database - SQLite3'
TYPE = 'database'
ICON = 'gen-database'
DESCRIPTION = 'Manage SQLite3 databases'
LONG_DESCRIPTION = ''
CATEGORIES = [
    {
        "primary": "Databases",
        "secondary": []
    }
]
VERSION = '1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "SQLite Consortium"
APP_HOMEPAGE = "https://www.sqlite.org/"
LOGO = False

# Plugin parameters
MODULES = ['main']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "SQLite3",
            "package": "sqlite3",
            "binary": "sqlite3"
        }
    ]
}
GENERATION = 1

# Database metadata
DB_NAME = 'SQLite3'
DB_PLUGIN = 'SQLite3'
DB_TASK = ''
MULTIUSER = False
REQUIRES_CONN = False
