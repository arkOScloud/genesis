# Plugin metadata
NAME = 'Database - MariaDB'
TYPE = 'database'
ICON = 'gen-database'
DESCRIPTION = 'Manage MariaDB/MySQL databases'
LONG_DESCRIPTION = ''
CATEGORIES = [
    {
        "primary": "Databases",
        "secondary": []
    }
]
VERSION = '2.2'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "MariaDB Foundation"
APP_HOMEPAGE = "https://mariadb.org/"
LOGO = False

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

# Database metadata
DB_NAME = 'MariaDB'
DB_PLUGIN = 'MariaDB'
DB_TASK = 'mysqld'
MULTIUSER = True
REQUIRES_CONN = True
