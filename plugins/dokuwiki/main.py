from genesis.com import Plugin, implements
from genesis import apis
from genesis.utils import shell

import nginx
import os

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
        shell('chown -R http ' + path)
        # TODO: put_message('info', 'Please go to
        # TODO: http://YOURADDRESS/install.php to configure DokuWiki.')

    def pre_remove(self, site):
        pass

    def post_remove(self, site):
        pass

    def ssl_enable(self, path, cfile, kfile):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s' % name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                self.addtoblock[0].add(
                    nginx.Key('proxy_set_header',
                              'X-Forwarded-For $proxy_add_x_forwarded_for'),
                    nginx.Key('proxy_set_header',
                              'X-Forwarded-Proto $scheme'),
                )
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s' % name)

    def ssl_disable(self, path):
        name = os.path.basename(path)
        n = nginx.loadf('/etc/nginx/sites-available/%s' % name)
        for x in n.servers:
            if x.filter('Location', '/'):
                x.remove(x.filter('Location', '/')[0])
                x.add(self.addtoblock[0])
                nginx.dumpf(n, '/etc/nginx/sites-available/%s' % name)

    def update(self, path, pkg, ver):
        pass
        # TODO update