import re
import os

from genesis.ui import *
from genesis.com import implements
from genesis.api import *
from genesis.utils import can_be_int, str_fsize

import backend


class FSPlugin(CategoryPlugin):
    text = 'Filesystems'
    iconfont = 'gen-storage'
    folder = 'advanced'

    def on_init(self):
        self.fstab = backend.read()
        self._devs, self._vdevs = self._fsc.get_filesystems()

    def on_session_start(self):
        self._editing = -1
        self._tab = 0
        self._fsc = backend.FSControl(self.app)
        self._add = None
        self._addenc = None
        self._auth = None

    def get_ui(self):
        ui = self.app.inflate('filesystems:main')

        t = ui.find('vdlist')

        for x in self._vdevs:
            t.append(UI.DTR(
                UI.Iconfont(iconfont=x.icon),
                UI.Label(text=x.name),
                UI.Label(text='Encrypted Disk' if x.fstype == 'crypt' else 'Virtual Disk'),
                UI.Label(text=str_fsize(x.size)),
                UI.Label(text=x.mount if x.mount else 'Not Mounted'),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-key', 
                        text='Encrypt Disk', 
                        id=('ecvd/' + str(self._vdevs.index(x))),
                        warning='Are you sure you wish to encrypt virtual disk %s? This will erase ALL data on the disk, and is irreversible.'%x.name
                    ) if x.fstype != 'crypt' else None,
                    UI.TipIcon(iconfont='gen-arrow-down-3' if x.mount else 'gen-arrow-up-3', 
                        text='Unmount' if x.mount else 'Mount', 
                        id=('umvd/' if x.mount else 'mvd/') + str(self._vdevs.index(x))
                    ) if x.mount != '/' else None,
                    UI.TipIcon(iconfont='gen-cancel-circle', 
                        text='Delete', 
                        id=('delvd/' + str(self._vdevs.index(x))), 
                        warning='Are you sure you wish to delete virtual disk %s?' % (x.name)
                    ) if x.delete else None,
                )
            ))

        t = ui.find('pdlist')

        for x in self._devs:
            if x.fstype == 'disk':
                fstype = 'Physical Disk'
            elif x.fstype == 'rom':
                fstype = 'Optical Disk Drive'
            elif x.fstype == 'part':
                fstype = 'Disk Partition'
            elif x.fstype == 'loop':
                fstype = 'Loopback'
            else:
                fstype = 'Unknown'
            t.append(UI.DTR(
                UI.Iconfont(iconfont=x.icon),
                UI.Label(text=x.name, bold=False if x.parent else True),
                UI.Label(text=fstype),
                UI.Label(text=str_fsize(x.size)),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-arrow-down-3' if x.mount else 'gen-arrow-up-3', 
                        text='Unmount' if x.mount else 'Mount', 
                        id=('umd/' if x.mount else 'md/') + str(self._devs.index(x))
                    ) if x.mount != '/' and x.fstype != 'disk' else None,
                )
            ))

        t = ui.find('list')

        for u in self.fstab:
            t.append(UI.DTR(
                    UI.Label(text=u.src, bold=True),
                    UI.Label(text=u.dst),
                    UI.Label(text=u.fs_type),
                    UI.Label(text=u.options),
                    UI.Label(text=str(u.dump_p)),
                    UI.Label(text=str(u.fsck_p)),
                    UI.HContainer(
                        UI.TipIcon(iconfont='gen-pencil-2', id='edit/'+str(self.fstab.index(u)), text='Edit'),
                        UI.TipIcon(iconfont='gen-cancel-circle', id='del/'+str(self.fstab.index(u)), text='Delete', warning='Remove %s from fstab'%u.src)
                    ),
                ))

        if self._editing != -1:
            try:
                e = self.fstab[self._editing]
            except:
                e = backend.Entry()
                e.src = '/dev/sda1'
                e.dst = '/tmp'
                e.options = 'none'
                e.fs_type = 'none'
                e.dump_p = 0
                e.fsck_p = 0
            self.setup_ui_edit(ui, e)
        else:
            ui.remove('dlgEdit')

        if self._add:
            ui.append('main', UI.DialogBox(
                UI.FormLine(
                    UI.TextInput(name='addname', id='addname'),
                    text='Virtual disk name'
                ),
                UI.FormLine(
                    UI.TextInput(name='addsize', id='addsize'),
                    text='Disk size (in MB)'
                ),
                UI.FormLine(
                    UI.EditPassword(id='passwd', value='Click to add password'),
                    text='Password'
                ) if self._add == 'enc' else None,
                id='dlgAdd'
            ))

        if self._enc:
            ui.append('main', UI.DialogBox(
                UI.FormLine(
                    UI.EditPassword(id='encpasswd', value='Click to add password'),
                    text='Password'
                ),
                id='dlgEnc'
            ))

        if self._auth:
            ui.append('main', UI.DialogBox(
                UI.FormLine(
                    UI.Label(text=self._auth.name),
                    text='For disk:'
                ),
                UI.FormLine(
                    UI.TextInput(name='authpasswd', password=True),
                    text='Password'
                ), id='dlgAuth'
            ))

        return ui

    def get_ui_sources_list(self, e):
        lst = UI.Select(name='disk')
        cst = True
        for p in backend.list_partitions():
            s = p
            try:
                s += ': %s partition %s' % (backend.get_disk_vendor(p), p[-1])
            except:
                pass
            sel = e != None and e.src == p
            cst &= not sel
            lst.append(UI.SelectOption(value=p, text=s, selected=sel))
        for p in backend.list_partitions():
            u = backend.get_partition_uuid_by_name(p)
            if u != '':
                s = 'UUID=' + u
                sel = e != None and e.src == s
                cst &= not sel
                lst.append(UI.SelectOption(value=s, text=p+': '+u , selected=sel))

        lst.append(UI.SelectOption(text='proc', value='proc', selected=e.src=='proc'))
        cst &= e.src != 'proc'
        lst.append(UI.SelectOption(text='Custom', value='custom', selected=cst))
        return lst, cst

    def setup_ui_edit(self, ui, e):
        opts = e.options.split(',')
        bind = False
        ro = False
        loop = False
        if 'bind' in opts:
            opts.remove('bind')
            bind = True
        if 'ro' in opts:
            opts.remove('ro')
            ro = True
        if 'loop' in opts:
            opts.remove('loop')
            loop = True
        opts = ','.join(opts)

        lst,cst = self.get_ui_sources_list(e)
        ui.append('sources', lst)
        ui.find('src').set('value', e.src if cst else '')
        ui.find('mp').set('value', e.dst)
        ui.find('fs').set('value', e.fs_type)
        ui.find('opts').set('value', e.options)
        ui.find('ro').set('checked', ro)
        ui.find('bind').set('checked', bind)
        ui.find('loop').set('checked', loop)
        ui.find('dump_p').set('value', e.dump_p)
        ui.find('fsck_p').set('value', e.fsck_p)

    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'adisk':
            self._tab = 0
            self._add = 'reg'
        if params[0] == 'aedisk':
            self._tab = 0
            self._add = 'enc'
        if params[0] == 'add':
            self._editing = len(self.fstab)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self.fstab.pop(int(params[1]))
            backend.save(self.fstab)
        if params[0] == 'ecvd':
            self._enc = self._vdevs[int(params[1])]
        if params[0] == 'md':
            self._tab = 1
            try:
                self._fsc.mount(self._devs[int(params[1])])
                self.put_message('info', 'Disk mounted successfully')
            except Exception, e:
                self.put_message('err', str(e))
        if params[0] == 'umd':
            self._tab = 1
            try:
                self._fsc.umount(self._devs[int(params[1])], rm=True)
                self.put_message('info', 'Disk unmounted successfully')
            except Exception, e:
                self.put_message('err', str(e))
        if params[0] == 'mvd':
            if self._vdevs[int(params[1])].fstype == 'crypt':
                self._auth = self._vdevs[int(params[1])]
            else:
                try:
                    self._fsc.mount(self._vdevs[int(params[1])])
                    self.put_message('info', 'Virtual disk mounted successfully')
                except Exception, e:
                    self.put_message('err', str(e))
        if params[0] == 'umvd':
            try:
                self._fsc.umount(self._vdevs[int(params[1])], rm=True)
                self.put_message('info', 'Virtual disk unmounted successfully')
            except Exception, e:
                self.put_message('err', str(e))
        if params[0] == 'delvd':
            try:
                self._fsc.delete(self._vdevs[int(params[1])])
                self.put_message('info', 'Virtual disk deleted successfully')
            except Exception, e:
                self.put_message('err', str(e))

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAdd':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('addname', '')
                size = vars.getvalue('addsize', '')
                passwd = vars.getvalue('passwd', '')
                if not name or not size:
                    self.put_message('err', 'Must choose a name and size')
                elif name in [x.name for x in self._vdevs]:
                    self.put_message('err', 'You already have a virtual disk with that name')
                elif re.search('\.|-|`|\\\\|\/|[ ]', name):
                    self.put_message('err', 'Disk name must not contain spaces, dots, dashes or special characters')
                elif not can_be_int(size):
                    self.put_message('err', 'Size must be a number in megabytes')
                elif self._add == 'enc' and not passwd:
                    self.put_message('err', 'Must choose a password')
                elif self._add == 'enc' and passwd != vars.getvalue('passwdb', ''):
                    self.put_message('err', 'Passwords must match')
                elif self._add == 'enc':
                    x = self._fsc.add_vdisk(name, size)
                    self._fsc.encrypt_vdisk(x, passwd, mount=True)
                else:
                    self._fsc.add_vdisk(name, size, mount=True)
            self._add = None
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                e = backend.Entry()
                if vars.getvalue('disk', 'custom') == 'custom':
                    e.src = vars.getvalue('src', 'none')
                else:
                    e.src = vars.getvalue('disk', 'none')
                e.dst = vars.getvalue('mp', 'none')
                e.fs_type = vars.getvalue('fs', 'none')
                e.options = vars.getvalue('opts', '')
                if vars.getvalue('bind', '0') == '1':
                    e.options += ',bind'
                if vars.getvalue('loop', '0') == '1':
                    e.options += ',loop'
                if vars.getvalue('ro', '0') == '1':
                    e.options += ',ro'
                e.options = e.options.strip(',')
                if e.options.startswith('none,'):
                    e.options = e.options[5:]

                e.dump_p = int(vars.getvalue('dump_p', '0'))
                e.fsck_p = int(vars.getvalue('fsck_p', '0'))
                try:
                    self.fstab[self._editing] = e
                except:
                    self.fstab.append(e)
                backend.save(self.fstab)
            self._editing = -1
        if params[0] == 'dlgAuth':
            if vars.getvalue('action', '') == 'OK':
                try:
                    self._fsc.mount(self._auth, vars.getvalue('authpasswd', ''))
                    self.put_message('info', 'Virtual disk decrypted and mounted successfully')
                except Exception, e:
                    self.put_message('err', str(e))
                self._auth = None
        if params[0] == 'dlgEnc':
            if vars.getvalue('action', '') == 'OK':
                passwd = vars.getvalue('encpasswd', '')
                if passwd != vars.getvalue('encpasswdb', ''):
                    self.put_message('err', 'Passwords must match')
                else:
                    try:
                        self._fsc.umount(self._enc)
                        self._fsc.encrypt_vdisk(self._enc, passwd, mount=True)
                        self.put_message('info', 'Virtual disk encrypted and mounted successfully')
                    except Exception, e:
                        self.put_message('err', str(e))
            self._enc = None
