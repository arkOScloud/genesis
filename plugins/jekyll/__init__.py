# Plugin metadata
NAME = 'Jekyll'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Run a statically-generated website or blog'
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Blogs", "Websites", "Static Sites"]
    }
]
VERSION = '1'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "Tom Preson-Werner, Nick Quaranto et al",
APP_HOMEPAGE = "http://jekyllrb.com/",

# Plugin parameters
MODULES = ['main']
PLATFORMS = ['any']
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "nginx",
            "package": "nginx",
            "binary": "nginx"
        },
        {
            "type": "app",
            "name": "ruby",
            "package": "ruby",
            "binary": "ruby"
        }
    ]
}
GENERATION = 1
