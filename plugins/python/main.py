import os
import stat
import shutil

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.com import Plugin, Interface, implements
from genesis.utils import shell, shell_cs


class PythonLangAssist(Plugin):
    implements(apis.langassist.ILangMgr)
    name = 'Python'

    def install(self, *mods):
        s = shell_cs('pip%s install %s' % \
            ('2' if self.app.platform in ['arkos', 'arch'] else '',
                ' '.join(x for x in mods)))
        if s[0] != 0:
            self.app.log.error('Failed to install %s via PyPI; %s'%(' '.join(x for x in mods),s[1]))
            raise Exception('Failed to install %s via PyPI, check logs for info'%' '.join(x for x in mods))

    def remove(self, *mods):
        s = shell_cs('pip%s uninstall %s' % \
            ('2' if self.app.platform in ['arkos', 'arch'] else '',
                ' '.join(x for x in mods)))
        if s[0] != 0:
            self.app.log.error('Failed to remove %s via PyPI; %s'%(' '.join(x for x in mods),s[1]))
            raise Exception('Failed to remove %s via PyPI, check logs for info'%' '.join(x for x in mods))

    def is_installed(self, name):
        s = shell('pip%s freeze'%'2' if self.app.platform in ['arkos', 'arch'] else '')
        for x in s.split('\n'):
            if name in x.split('==')[0]:
                return True
        return False

    def add_django_site(self, name, path, user, group):
        shell('cd %s; django-admin.py startproject %s' % (path,name))
        gconf = '#! /bin/bash\n\n'
        gconf += 'NAME="%s"\n' % name
        gconf += 'SOCKFILE=%s\n' % os.path.join(path, 'gunicorn.sock')
        gconf += 'USER=%s\n' % user
        gconf += 'GROUP=%s\n' % group
        gconf += 'NUM_WORKERS=3\n'
        gconf += 'DJANGODIR=%s\n' % path
        gconf += 'DJANGO_SETTINGS_MODULE=%s.settings\n' % name
        gconf += 'DJANGO_WSGI_MODULE=%s.wsgi\n\n' % name
        gconf += 'export PYTHONPATH=$DJANGODIR:$PYTHONPATH\n\n'
        gconf += 'echo "Starting $NAME as `whoami`"\n\n'
        gconf += 'exec gunicorn ${DJANGO_WSGI_MODULE}:application \ \n'
        gconf += '--name $NAME --workers $NUM_WORKERS \ \n'
        gconf += '--user=$USER --group=$GROUP \ \n'
        gconf += '--log-level=debug --bind=unix:$SOCKFILE\n'
        open(os.path.join(path, 'gunicorn'), 'w').write(gconf)
        st = os.stat(os.path.join(path, 'gunicorn'))
        os.chmod(os.path.join(path, 'gunicorn'), st.st_mode | 0111)
        s = filter(lambda x: x.id == 'supervisor',
            self.app.grab_plugins(apis.orders.IListener))
        if s:
            s[0].order('new', name, 'program', 
                [('directory', path), ('user', user), 
                ('command', os.path.join(path, 'gunicorn')),
                ('stdout_logfile', os.path.join(path, '%s_logfile.log'%name)),
                ('stderr_logfile', os.path.join(path, '%s_logfile.log'%name))])

    def remove_django_site(self, name, path):
        s = filter(lambda x: x.id == 'supervisor',
            self.app.grab_plugins(apis.orders.IListener))
        if s:
            s[0].order('del', name)
        shutil.rmtree(path)
