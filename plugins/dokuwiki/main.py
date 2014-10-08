from genesis.com import Plugin, implements
from genesis import apis

import nginx

class DokuWiki(Plugin):
    implements(apis.webapps.IWebapp)
    name = 'DokuWiki'
    icon = 'gen-book'

    addtoblock = [
        nginx.Location('/(data|conf|bin|inc)/',
            nginx.Key('deny', 'all')
        )
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