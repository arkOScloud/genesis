# Plugin metadata
NAME = 'Database - MariaDB'
TYPE = 'database'
ICON = 'gen-database'
DESCRIPTION = 'Manage MariaDB/MySQL databases'
CATEGORIES = [
    {
        "primary": "Databases",
        "secondary": []
    }
]
VERSION = '2'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "MariaDB Foundation"
APP_HOMEPAGE = "https://mariadb.org/"

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
            "type": "module",
            "name": "MySQL-Python",
            "package": "mysql-python",
            "binary": "_mysql"
        }
    ]
}
GENERATION = 1
