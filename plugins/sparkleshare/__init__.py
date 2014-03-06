# Plugin metadata
NAME = 'SparkleShare'
TYPE = 'plugin'
ICON = 'gen-upload-2'
DESCRIPTION = 'Revision-controlled file storage and sync'
LONG_DESCRIPTION = ('SparkleShare is an Open Source collaboration and '
    'sharing tool that is designed to keep things simple and to stay out '
    'of your way. It allows you to instantly sync with Git repositories '
    'and has clients available for Linux distributions, Mac and Windows.')
CATEGORIES = [
    {
        "primary": "File Storage",
        "secondary": ["Documents", "Collaboration"]
    },
    {
        "primary": "Project Management",
        "secondary": []
    }
]
VERSION = '0'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "SparkleShare"
APP_HOMEPAGE = "http://sparkleshare.org/"
LOGO = False

SERVICES = []

# Plugin parameters
MODULES = ["main", "backend"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "Git",
            "package": "git",
            "binary": "git"
        }
    ]
}
GENERATION = 1

