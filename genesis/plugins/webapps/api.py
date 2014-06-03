from genesis.com import *
from genesis import apis

import ConfigParser
import glob
import nginx
import os
import re


class Webapp(object):
    name = ''
    stype = ''
    ssl = False
    ssl_able = True
    addr = ''
    port = ''
    path = ''
    php = False
    sclass = None
    enabled = False


class Webapps(apis.API):
    def __init__(self, app):
        self.app = app

    class IWebapp(Interface):
        def pre_install(self, name, vars):
            pass

        def post_install(self, name, path, vars):
            pass

        def pre_remove(self, name, path):
            pass

        def post_remove(self, name):
            pass

        def ssl_enable(self, path, cfile, kfile):
            pass

        def ssl_disable(self, path):
            pass

    def get_apptypes(self):
        applist = []
        for plugin in self.app.grab_plugins(apis.webapps.IWebapp):
            applist.append(plugin)
        return applist

    def get_sites(self):
        applist = []
        if not os.path.exists('/etc/nginx/sites-available'):
            os.makedirs('/etc/nginx/sites-available')
        if not os.path.exists('/etc/nginx/sites-enabled'):
            os.makedirs('/etc/nginx/sites-enabled')

        for site in glob.glob('/etc/nginx/sites-available/.*.ginf'):
            g = ConfigParser.SafeConfigParser()
            g.read(site)
            w = Webapp()
            # Set default values and regexs to use
            w.name = g.get('website', 'name')
            w.addr = False
            w.port = '80'
            w.stype = 'Unknown'
            w.path = os.path.join('/etc/nginx/sites-available', g.get('website', 'name'))
            rport = re.compile('(\\d+)\s*(.*)')

            # Get actual values
            try:
                s = None
                c = nginx.loadf(w.path)
                w.stype = g.get('website', 'stype')
                # Get the right serverblock - SSL if it's here
                for x in c.servers:
                    if 'ssl' in x.filter('Key', 'listen')[0].value:
                        s = x
                        break
                if not s:
                    s = c.servers[0]
                w.port, w.ssl = re.match(rport, s.filter('Key', 'listen')[0].value).group(1, 2)
                w.addr = s.filter('Key', 'server_name')[0].value
                w.path = s.filter('Key', 'root')[0].value
                w.php = True if 'php' in s.filter('Key', 'index')[0].value else False
            except IndexError:
                pass
            w.dbengine = g.get('website', 'dbengine', None)
            w.dbname = g.get('website', 'dbname', None)
            w.dbuser = g.get('website', 'dbuser', None)

            w.enabled = True if os.path.exists(os.path.join('/etc/nginx/sites-enabled', g.get('website', 'name'))) else False

            w.sclass = self.get_interface(w.stype)
            w.sinfo = self.get_info(w.stype)
            w.ssl_able = w.sinfo.ssl if hasattr(w.sinfo, 'ssl') else False

            applist.append(w)
        return applist

    def get_info(self, name):
        cs = filter(lambda x: x.__class__.__name__ == name,
            self.app.grab_plugins(apis.webapps.IWebapp))
        return cs[0].plugin_info if len(cs) else None

    def get_interface(self, name):
        cs = filter(lambda x: x.__class__.__name__ == name,
            self.app.grab_plugins(apis.webapps.IWebapp))
        return cs[0] if len(cs) else None
