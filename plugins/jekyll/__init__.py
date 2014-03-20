# Plugin metadata
NAME = 'Jekyll'
TYPE = 'webapp'
ICON = 'gen-earth'
DESCRIPTION = 'Run a statically-generated website or blog'
LONG_DESCRIPTION = ('Jekyll is a simple, blog-aware, static site '
    'generator. It takes a template directory containing raw '
    'text files in various formats, runs it through Markdown '
    '(or Textile) and Liquid converters, and spits out a '
    'complete, ready-to-publish static website suitable for '
    'serving with your favorite web server.')
CATEGORIES = [
    {
        "primary": "Websites",
        "secondary": ["Blogs", "Websites", "Static Sites"]
    }
]
VERSION = '1.1'

AUTHOR = 'arkOS'
HOMEPAGE = 'https://arkos.io'
APP_AUTHOR = "Tom Preson-Werner, Nick Quaranto et al"
APP_HOMEPAGE = "http://jekyllrb.com/"
LOGO = True

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
        },
        {
            "type": "plugin",
            "name": "Ruby",
            "package": "ruby"
        }
    ]
}
GENERATION = 1

# Webapp metadata
WA_PLUGIN = 'Jekyll'
DPATH = 'https://pkg.arkos.io/resources/jekyll-sample.tar.gz'
DBENGINE = ''
PHP = False
NOMULTI = False
SSL = True
