# Plugin metadata
NAME = 'Scheduled Tasks'
TYPE = 'plugin'
ICON = 'gen-alarm'
DESCRIPTION = 'Manage scheduled tasks and system automation'
CATEGORIES = [
    {
        "primary": "Utilities",
        "secondary": ["Automation"]
    }
]
VERSION = '1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'

# Plugin parameters
MODULES = ['main', 'backend']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "cron",
            "package": "cronie",
            "binary": "crontab"
        }
    ]
}
GENERATION = 1
