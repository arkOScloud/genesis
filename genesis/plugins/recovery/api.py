import os
import glob
import tempfile
import shutil
import time
import tempfile

from genesis.com import *
from genesis.api import *
from genesis.utils import shell, shell_status


class BackupRevision:
    def __init__(self, rev, date):
        self.revision = rev
        self.date = time.strftime('%a, %d %b %Y %H:%M:%S', date)
        self._date = date


class Manager(Plugin):
    def __init__(self):
        try:
            self.dir = self.config.get('recovery', 'dir')
        except:
            self.dir = '/var/backups/genesis'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        
    def list_backups(self, id):
        r = []
        if not os.path.exists(os.path.join(self.dir, id)):
            return r
            
        for x in os.listdir(os.path.join(self.dir, id)):
            r.append(BackupRevision(
                        x.split('.')[0], 
                        time.localtime(
                            os.path.getmtime(
                                os.path.join(self.dir, id, x)
                            )
                         )
                     ))
        return reversed(sorted(r, key=lambda x: x._date))

    def find_provider(self, id):
        return ConfManager.get().get_configurable(id)
        
    def delete_backup(self, id, rev):
        os.unlink(os.path.join(self.dir, id, rev+'.tar.gz'))
        
    def backup_all(self):
        errs = []
        for x in self.app.grab_plugins(IConfigurable):
            try:
                self.backup(x)
            except:
                errs.append(x.name)
        return errs
        
    def backup(self, provider):
        try:
            os.makedirs(os.path.join(self.dir, provider.id))
        except:
            pass
        dir = tempfile.mkdtemp()
        
        try:
            for f in provider.list_files():
                for x in glob.glob(f):
                    xdir = os.path.join(dir, os.path.split(x)[0][1:])
                    shell('mkdir -p \'%s\'' % xdir)
                    shell('cp -r \'%s\' \'%s\'' % (x, xdir))

            metafile = open(dir + '/genesis-backup', 'w')
            metafile.write(provider.id)
            metafile.close()

            if shell_status('cd %s; tar czf backup.tar.gz *'%dir) != 0:
                raise Exception()
            
            name = 0
            try:
                name = int(os.listdir(self.dir+'/'+provider.id)[0].split('.')[0])
            except:
                pass
            
            while os.path.exists('%s/%s/%i.tar.gz'%(self.dir,provider.id,name)):
                name += 1
            
            shutil.move('%s/backup.tar.gz'%dir, '%s/%s/%s.tar.gz'%(self.dir,provider.id,name))
        except:
            raise
        finally:
            shutil.rmtree(dir)
        
    def restore(self, provider, revision):
        dir = tempfile.mkdtemp()
        shutil.copy('%s/%s/%s.tar.gz'%(self.dir,provider.id,revision), '%s/backup.tar.gz'%dir)
        for f in provider.list_files():
            for x in glob.glob(f):
                os.unlink(x)
        if shell_status('cd %s; tar xf backup.tar.gz -C / --exclude genesis-backup'%dir) != 0:
            raise Exception()
        os.unlink('%s/backup.tar.gz'%dir)
        shutil.rmtree(dir)

    def upload(self, file):
        dir = '/var/backups/genesis/'

        # Get the backup then read its metadata
        tempdir = tempfile.mkdtemp()
        temparch = os.path.join(tempdir, 'backup.tar.gz')
        open(temparch, 'wb').write(file.value)

        shell('tar xzf ' + temparch + ' -C ' + tempdir)
        bfile = open(os.path.join(tempdir, 'genesis-backup'), 'r')
        name = bfile.readline()
        bfile.close()

        # Name the file and do some work
        if not os.path.exists(os.path.join(dir, name)):
            os.makedirs(os.path.join(dir, name))
        priors = os.listdir(dir + name)
        thinglist = []
        for thing in priors:
            thing = thing.split('.')
            thinglist.append(thing[0])
        newver = int(max(thinglist)) + 1 if thinglist else 0

        shell('cp %s %s' % (temparch, os.path.join(dir, name, str(newver) + '.tar.gz')))
        shell('rm -r ' + tempdir)

    def get_backups(self):
        dir = tempfile.mkdtemp()
        temparch = os.path.join(dir, 'backup-all.tar.gz')
        shell('tar czf ' + temparch + ' -C /var/backups/ genesis')
        size = os.path.getsize(temparch)

        f = open(temparch, 'rb')
        arch = f.read()
        f.close()
        shell('rm -r ' + dir)
        return (size, arch)

class RecoveryHook (ConfMgrHook):
    def finished(self, cfg):
        Manager(self.app).backup(cfg)
        
