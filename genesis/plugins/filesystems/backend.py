import re
import os
import glob

from genesis.api import *
from genesis.com import *
from genesis.utils import *

import losetup


class Filesystem(object):
    name = ''
    dev = ''
    lodev = ''
    fstype = 'disk'
    icon = ''
    size = 0
    mount = ''
    parent = None
    delete = True


class FSControl(Plugin):
    def get_filesystems(self):
        devs, vdevs, loops = [],[],[]
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
            elif x[5] == 'loop':
                f.icon = 'gen-loop-2'
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
            elif f.fstype == 'loop':
                loops.append(f)
            else:
                devs.append(f)

        l = losetup.get_loop_devices()
        l = [l[x] for x in l if l[x].is_used()]
        if not os.path.exists('/vdisk'):
            os.mkdir('/vdisk')
        for x in glob.glob('/vdisk/*.img'):
            f = Filesystem()
            for y in l:
                if y.get_filename() == x:
                    for z in loops:
                        if z.dev == y.device:
                            f = z
                            f.delete = True
            f.name = os.path.splitext(os.path.split(x)[1])[0]
            f.lodev = f.dev
            f.dev = x
            f.fstype = 'vdisk'
            f.icon = 'gen-embed'
            f.size = os.path.getsize(x)
            vdevs.append(f)
        for x in glob.glob('/vdisk/*.crypt'):
            f = Filesystem()
            for y in l:
                if y.get_filename() == x:
                    for z in loops:
                        if z.dev == y.device:
                            f = z
                            f.delete = True
            f.name = os.path.splitext(os.path.split(x)[1])[0]
            f.lodev = f.dev
            f.dev = x
            f.fstype = 'crypt'
            f.icon = 'gen-lock'
            f.size = os.path.getsize(x)
            vdevs.append(f)
        return devs, vdevs

    def add_vdisk(self, name, size, mkfs=True, mount=False):
        with open(os.path.join('/vdisk', name+'.img'), 'wb') as f:
            written = 0
            while (int(size)*1048576) > written:
                written += 1024
                f.write(os.urandom(1024))
            f.close()
        if mkfs:
            l = losetup.find_unused_loop_device()
            l.mount(os.path.join('/vdisk', name+'.img'))
            s = shell_cs('mkfs.ext4 %s'%l.device)
            if s[0] != 0:
                raise Exception('Failed to format loop device: %s'%s[1])
            l.unmount()
        fs = Filesystem()
        fs.name = name
        fs.dev = os.path.join('/vdisk', name+'.img')
        fs.fstype = 'vdisk'
        if mount:
            self.mount(fs)
        return fs

    def encrypt_vdisk(self, fs, passwd, opts={'cipher': 'aes-xts-plain64', 'keysize': '256', 'hash': 'sha1'}, move=True, mount=False):
        opts = '-c %s -s %s -h %s'%(opts['cipher'], str(opts['keysize']), opts['hash'])
        l = losetup.get_loop_devices()
        if move:
            os.rename(os.path.join('/vdisk', fs.name+'.img'), os.path.join('/vdisk', fs.name+'.crypt'))
        dev = losetup.find_unused_loop_device()
        dev.mount(os.path.join('/vdisk', fs.name+'.crypt'))
        fs.dev = os.path.join('/vdisk', fs.name+'.crypt')
        s = shell_cs('echo "%s" | cryptsetup %s luksFormat %s'%(passwd,opts,dev.device), stderr=True)
        if s[0] != 0:
            if move:
                dev.unmount()
                os.rename(os.path.join('/vdisk', fs.name+'.crypt'), os.path.join('/vdisk', fs.name+'.img'))
            raise Exception('Failed to encrypt %s: %s'%(fs.name, s[1]))
        fs.fstype = 'crypt'
        s = shell_cs('echo "%s" | cryptsetup luksOpen %s %s'%(passwd,dev.device,fs.name), stderr=True)
        if s[0] != 0:
            dev.unmount()
            raise Exception('Failed to decrypt %s: %s'%(fs.name, s[1]))
        s = shell_cs('mkfs.ext4 /dev/mapper/%s'%fs.name, stderr=True)
        self.umount(fs)
        if s[0] != 0:
            raise Exception('Failed to format loop device: %s'%s[1])
        if mount:
            fs.fstype = 'crypt'
            self.mount(fs, passwd)

    def mount(self, fs, passwd=''):
        dev = losetup.find_unused_loop_device()
        dev.mount(fs.dev)
        if not os.path.isdir(os.path.join('/media', fs.name)):
            os.mkdir(os.path.join('/media', fs.name))
        if fs.fstype == 'crypt':
            s = shell_cs('echo "%s" | cryptsetup luksOpen %s %s'%(passwd,dev.device,fs.name), stderr=True)
            if s[0] != 0:
                dev.unmount()
                raise Exception('Failed to decrypt %s: %s'%(fs.name, s[1]))
            s = shell_cs('mount /dev/mapper/%s %s'%(fs.name, os.path.join('/media', fs.name)), stderr=True)
            if s[0] != 0:
                shell('cryptsetup luksClose %s'%fs.name)
                dev.unmount()
                raise Exception('Failed to mount %s: %s'%(fs.name, s[1]))
        else:
            s = shell_cs('mount %s %s'%(dev.device, os.path.join('/media', fs.name)), stderr=True)
            if s[0] != 0:
                dev.unmount()
                raise Exception('Failed to mount %s: %s'%(fs.name, s[1]))

    def umount(self, fs, rm=False):
        if not fs.mount:
            return
        dev = None
        l = losetup.get_loop_devices()
        for x in l:
            if l[x].is_used() and l[x].get_filename() == fs.dev:
                dev = l[x]
                break
        if dev and fs.fstype == 'crypt':
            s = shell_cs('umount /dev/mapper/%s'%fs.name, stderr=True)
            if s[0] != 0:
                raise Exception('Failed to unmount %s: %s'%(fs.name, s[1]))
            shell('cryptsetup luksClose %s'%fs.name)
            dev.unmount()
        elif dev:
            s = shell_cs('umount %s'%dev.device, stderr=True)
            if s[0] != 0:
                raise Exception('Failed to unmount %s: %s'%(fs.name, s[1]))
            dev.unmount()
        if rm:
            os.unlink(fs.mount)

    def delete(self, fs):
        self.umount(fs)
        if fs.fstype == 'crypt':
            os.unlink(os.path.join('/vdisk', fs.name+'.crypt'))
        else:
            os.unlink(os.path.join('/vdisk', fs.name+'.img'))


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
