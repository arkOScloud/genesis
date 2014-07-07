import nginx

from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell

import os
import shutil


class Gitweb(Plugin):
    implements(apis.webapps.IWebapp)

    addtoblock = [
        nginx.Location('/',
            nginx.Key('index', 'gitweb.cgi'),
            nginx.Key('include', 'fastcgi_params'),
            nginx.Key('gzip', 'off'),
            nginx.Key('fastcgi_param', 'GITWEB_CONFIG /etc/conf.d/gitweb.conf'),
            nginx.If('($uri ~ "/gitweb.cgi")',
                nginx.Key('fastcgi_pass', 'unix:/var/run/fcgiwrap.sock')
            )
        )
    ]

    def pre_install(self, name, vars):
        # Write a standard Gitweb config file
        if not os.path.exists('/etc/conf.d'):
            os.makedirs('/etc/conf.d')
        f = open('/etc/conf.d/gitweb.conf', 'w')
        oc = ['our $git_temp = "/tmp";\n',
            'our $projectroot = "'+vars.getvalue('gw-proot', '')+'";\n',
            'our @git_base_url_list = qw(git://'+vars.getvalue('hostname', '')+' http://git@'+vars.getvalue('hostname', '')+');\n'
        ]
        f.writelines(oc)
        f.close()

    def post_install(self, name, path, vars, dbinfo={}):
        svc = self.app.get_backend(apis.services.IServiceManager)

        f = open('/usr/lib/systemd/system/fcgiwrap.service', 'w')
        oc = ['[Unit]\n',
            'Description=Simple server for running CGI applications over FastCGI\n',
            'After=syslog.target network.target\n',
            '\n',
            '[Service]\n',
            'Type=forking\n',
            'Restart=on-abort\n',
            'PIDFile=/var/run/fcgiwrap.pid\n',
            'ExecStart=/usr/bin/spawn-fcgi -s /var/run/fcgiwrap.sock -P /var/run/fcgiwrap.pid -u http -g http -- /usr/sbin/fcgiwrap\n',
            'ExecStop=/usr/bin/kill -15 $MAINPID\n',
            '\n',
            '[Install]\n',
            'WantedBy=multi-user.target\n'
        ]
        f.writelines(oc)
        f.close()

        svc.enable('fcgiwrap')
        svc.start('fcgiwrap')

        if os.path.exists(os.path.join('/srv/http/webapps', name)):
            if os.path.isdir(os.path.join('/srv/http/webapps', name)):
                shutil.rmtree(os.path.join('/srv/http/webapps', name))
            else:
                os.unlink(os.path.join('/srv/http/webapps', name))
        os.symlink('/usr/share/gitweb', 
            os.path.join('/srv/http/webapps', name))

    def pre_remove(self, site):
        pass

    def post_remove(self, name):
        pass

    def ssl_enable(self, path, cfile, kfile):
        pass

    def ssl_disable(self, path):
        pass

    def update(self, path, pkg, ver):
        pass
