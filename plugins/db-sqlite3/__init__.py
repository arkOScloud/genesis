# Plugin metadata
NAME = 'Database - SQLite3'
TYPE = 'database'
ICON = 'gen-database'
DESCRIPTION = 'Manage SQLite3 databases'
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
