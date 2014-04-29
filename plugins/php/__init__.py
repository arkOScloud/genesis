# Plugin metadata
NAME = 'PHP'
TYPE = 'plugin'
ICON = 'gen-code'
DESCRIPTION = 'Extension functions for PHP websites'
CATEGORIES = [
    {
        "primary": "Management",
        "secondary": []
    }
]
VERSION = '0.2'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
LOGO = False

SERVICES = []

# Plugin parameters
MODULES = ["main"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
    	{
    	    "type": "app",
    	    "name": "PHP",
    	    "package": "php",
    	    "binary": None
    	},
        {
            "type": "app",
            "name": "PHP FastCGI",
            "package": "php-fpm",
            "binary": "php-fpm"
        }
    ]
}
GENERATION = 1
