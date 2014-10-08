from genesis.com import Plugin, implements
from genesis import apis

import nginx

class DokuWiki(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'DokuWiki'
    icon = 'gen-book'

    addtoblock = [
        nginx.Location('/',
            nginx.Key('index', 'doku.php'),
            nginx.Key('try_files', '$uri $uri/ @dokuwiki'),
        ),
        nginx.Location('~ /(data|conf|bin|inc)/',
            nginx.Key('deny', 'all')
        ),
        nginx.Location(r'~ /\.ht',
            nginx.Key('deny', 'all')
        ),
        nginx.Location('@dokuwiki',
            nginx.Key('rewrite', '^/_media/(.*) /lib/exe/fetch.php?media=$1 last'),
            nginx.Key('rewrite', '^/_detail/(.*) /lib/exe/detail.php?media=$1 last'),
            nginx.Key('rewrite', '^/_export/([^/]+)/(.*) /doku.php?do=export_$1&id=$2 last'),
            nginx.Key('rewrite', '^/(.*) /doku.php?id=$1 last'),
        ),
        nginx.Location(r'~ \.php$',
            nginx.Key('include', 'fastcgi_params'),
            nginx.Key('fastcgi_param', 'SCRIPT_FILENAME $document_root$fastcgi_script_name'),
            nginx.Key('fastcgi_pass', 'unix:/run/php-fpm/php-fpm.sock'),
        ),
    ]

    def pre_install(self, name, vars):
        pass

    def post_install(self, name, path, vars, dbinfo={}):
        pass

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

    def update(self, path, pkg, ver):
        pass