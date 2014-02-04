import re
import os
import glob

from genesis.api import *
from genesis.com import *
from genesis.utils import *


class Filesystem(object):
    name = ''
    dev = ''
    fstype = 'disk'
    icon = ''
    size = 0
    mount = ''
    parent = None
    delete = True


class FSControl(Plugin):
    def get_filesystems(self):
        devs, vdevs = [],[]
        fdisk = shell('lsblk -pbl').split('\n')

        for x in fdisk:
            if x.startswith('NAME') or not x.split():
                continue
            x = x.split()

            f = Filesystem()
            f.name = x[0].split('/')[-1]
            f.dev = x[0]
            f.size = int(x[3])
            f.fstype = x[5]
            if x[5] == 'part':
                f.icon = 'gen-arrow-down'
            elif x[5] == 'rom':
                f.icon = 'gen-cd'
            elif x[5] == 'crypt':
                f.icon = 'gen-lock'
                f.delete = False
            else:
                f.icon = 'gen-storage'
            f.mount = x[6] if len(x) >= 7 else ''
            for y in devs:
                if y.dev in f.dev:
                    f.parent = y
                    break
            if f.fstype == 'crypt':
                vdevs.append(f)
            else:
                devs.append(f)

        if not os.path.exists('/vdisk'):
            os.mkdir('/vdisk')
        for x in glob.glob('/vdisk/*.img'):
            f = Filesystem()
            f.name = os.path.splitext(os.path.split(x)[1])[0]
            f.dev = x
            f.fstype = 'vdisk'
            f.icon = 'gen-embed'
            f.size = os.path.getsize(x)
            vdevs.append(f)
        for x in glob.glob('/vdisk/*.crypt'):
            f = Filesystem()
            f.name = os.path.splitext(os.path.split(x)[1])[0]
            f.dev = x
            f.fstype = 'crypt'
            f.icon = 'gen-lock'
            f.size = os.path.getsize(x)
            vdevs.append(f)
        return devs, vdevs


class Entry:
    def __init__(self):
        self.src = ''
        self.dst = ''
        self.options = ''
        self.fs_type = ''
        self.dump_p = 0
        self.fsck_p = 0


def read():
    ss = ConfManager.get().load('filesystems', '/etc/fstab').split('\n')
    r = []

    for s in ss:
        if s != '' and s[0] != '#':
            try:
                s = s.split()
                e = Entry()
                try:
                    e.src = s[0]
                    e.dst = s[1]
                    e.fs_type = s[2]
                    e.options = s[3]
                    e.dump_p = int(s[4])
                    e.fsck_p = int(s[5])
                except:
                    pass
                r.append(e)
            except:
                pass

    return r

def save(ee):
    d = ''
    for e in ee:
        d += '%s\t%s\t%s\t%s\t%i\t%i\n' % (e.src, e.dst, e.fs_type, e.options, e.dump_p, e.fsck_p)
    ConfManager.get().save('filesystems', '/etc/fstab', d)
    ConfManager.get().commit('filesystems')

def list_disks():
    r = []
    for s in os.listdir('/dev'):
        if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
            r.append('/dev/' + s)
    return sorted(r)

def list_partitions():
    r = []
    for s in os.listdir('/dev'):
        if re.match('sd..$|hd..$|scd.$|fd.$', s):
            r.append('/dev/' + s)
    return sorted(r)

def get_disk_vendor(d):
    return ' '.join(shell('hdparm -I ' + d + ' | grep Model').split()[3:])

def get_partition_uuid_by_name(p):
    return shell('blkid -o value -s UUID ' + p).split('\n')[0]

def get_partition_name_by_uuid(u):
    return shell('blkid -U ' + u)


class FSConfigurable (Plugin):
    implements(IConfigurable)
    name = 'Filesystems'
    id = 'filesystems'

    def list_files(self):
        return ['/etc/fstab']
