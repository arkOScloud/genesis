"""
Python API for 'loop' Linux module.

This module allows Python program to mount file as loop device.


Some parts of this code based on util-linux-ng project (http://userweb.kernel.org/~kzak/util-linux-ng/)

Copyright (C) 2008 Sergey Kirillov, Rainboo Software
 
"""

__version__ = '2.0.7'

import os
import re
import stat
import struct
import array
import fcntl
#import _losetup

DEV_LOOP_PATH = "/dev/loop/"
DEV_PATH = "/dev/"
LOOPMAJOR = 7

class LosetupError(Exception):
    """Base class for all losetup exceptions"""
    pass

class NoLoopSupportError(LosetupError):
    """Loop support is not detected for running system""" 
    pass

class LoopNotFoundError(LosetupError):
    """Specified loop device is not found""" 
    pass

class LoopNotMountedError(LosetupError):
    """Loop device is not mounted error"""
    pass

class NotLoopError(LosetupError):
    """Specified device is not a loop device""" 
    pass


class Status64(object):
    _fmt = "=QQQQQLLLL64s64s32s2Q"
    size = struct.calcsize(_fmt)
    
    def __init__(self, buf=None):
        # If buf is None initialize with zeroes
        if buf is None:
            buf = array.array('B', [0] * self.size)
            
        data = struct.unpack(self._fmt, buf.tostring())
        i = iter(data)
        self.lo_device = i.next()
        self.lo_inode = i.next()
        self.lo_rdevice = i.next()
        self.lo_offset = i.next()
        self.lo_sizelimit = i.next()
        self.lo_number = i.next()
        self.lo_encrypt_type = i.next()
        self.lo_encrypt_key_size = i.next()
        self.lo_flags = i.next()
        self.lo_filename = i.next().rstrip('\0')
        self.lo_crypt_name = i.next().rstrip('\0')
        self.lo_encrypt_key = i.next()[:self.lo_encrypt_key_size]
        self.lo_init = (i.next(), i.next())


    def dump(self):
        return struct.pack(self._fmt, 
                           self.lo_device, 
                           self.lo_inode,
                           self.lo_rdevice, 
                           self.lo_offset, 
                           self.lo_sizelimit,
                           self.lo_number, 
                           self.lo_encrypt_type, 
                           self.lo_encrypt_key_size,
                           self.lo_flags,
                           self.lo_filename,
                           self.lo_crypt_name,
                           self.lo_encrypt_key,
                           self.lo_init[0],
                           self.lo_init[1])
    
class LoopDevice(object):
    
    LOOP_SET_FD = 0x4C00
    LOOP_CLR_FD = 0x4C01
    LOOP_SET_STATUS = 0x4C02
    LOOP_GET_STATUS = 0x4C03
    LOOP_SET_STATUS64 = 0x4C04
    LOOP_GET_STATUS64 = 0x4C05
    
    
    LO_FLAGS_READ_ONLY  = 1
    LO_FLAGS_USE_AOPS   = 2
    LO_FLAGS_AUTOCLEAR  = 4 # New in 2.6.25
    
    
    def __init__(self, device):
        self.device = device
        
        if not is_loop(device):
            raise NotLoopError("'%s' is not a loop device" % device)        
        
        
    def is_used(self):
        """Check if device is used"""
        try:
            status = self.get_status()
            return True
        except:
            return False
    
    def mount(self, target_path, offset=0, sizelimit=0):
        """Mount file to loop device"""
        status = Status64()
        status.lo_filename = target_path
        status.lo_offset = offset
        status.lo_sizelimit = sizelimit
        
        self._do_mount(target_path, status)

    def mount_ex(self, target_path, display_as):
        status = Status64()
        status.lo_filename = display_as
        
        self._do_mount(target_path, status)

    def unmount(self):
        """Unmount device"""
        try:
            fd = self._open_fd()
            self._do_unmount(fd)
        finally:
            os.close(fd)

    def get_filename(self):
        status = self.get_status()
        return status.lo_filename

    def get_status(self):
        try:
            fd = self._open_fd()
            return self._get_status64(fd)
        finally:
            os.close(fd)


    def _open_fd(self):
        return os.open(self.device, os.O_RDWR)

    def _do_mount(self, path, status):
        try:
            fd = self._open_fd()
            
            try:
                target_fd = os.open(path, os.O_RDWR)
            except IOError:
                status.lo_flags = self.LO_FLAGS_READ_ONLY
                target_fd = os.open(path, os.O_RDONLY)
    
            try:
                ret = fcntl.ioctl(fd, self.LOOP_SET_FD, target_fd)
            finally:
                os.close(target_fd)
                
                
            try:
                self._set_status64(fd, status)
            except:
                self._do_unmount(fd)
                raise
        finally:
            os.close(fd)
        
    def _do_unmount(self, fd):
        fcntl.ioctl(fd, self.LOOP_CLR_FD)
    
    def __repr__(self):
        return 'LoopDevice("%s")' % self.device
    
    def _get_status64(self, fd):
        buf = array.array('B', [0] * Status64.size)
        
        try:
            fcntl.ioctl(fd, self.LOOP_GET_STATUS64, buf, True)
        except IOError, e:
            if e.errno == 6:
                raise LoopNotMountedError("Loop device '%s' is not mounted" % self.device)
            else:
                raise
        
        return Status64(buf)

    def _set_status64(self, fd, status):
        data = status.dump()
        
        fcntl.ioctl(fd, self.LOOP_SET_STATUS64, data)
            
def is_loop(filename):
    """Check whether specified filename is a loop device"""
    st = os.stat(filename)
    return stat.S_ISBLK(st.st_mode) and (_major(st.st_rdev) == LOOPMAJOR)

                  
def find_unused_loop_device():
    """Find first unused loop device"""
    devs = get_loop_devices()
    for num, dev in _loop_devices.iteritems():
        if not dev.is_used():
            return dev
        
    raise LoopNotFoundError("Unable to find free loop device")

def get_loop_devices():
    global _loop_devices
    
    if _loop_devices is None:
        _loop_devices = _build_loop_devices()
        
    return _loop_devices


# Initialize loop devices list
_loop_devices = None

def _build_loop_devices():
    loop_devices = {}
    
    if os.path.isdir(DEV_LOOP_PATH):
        devs = os.listdir(DEV_LOOP_PATH)
        for num in devs:
            path = os.path.join(DEV_LOOP_PATH, num)
            if is_loop(path): 
                loop_devices[num] = LoopDevice(path)
    else:
        _loop_dev_re = re.compile("^loop(\d+)$")
        for d in os.listdir(DEV_PATH):
            m = _loop_dev_re.match(d)
            if not m:
                continue
            num = m.group(1)
            path = os.path.join(DEV_PATH, d)
            if is_loop(path): 
                loop_devices[num] = LoopDevice(path)
    return loop_devices

def _major(value):
    return (value >> 8) & 0xff;

def _minor(value):
    return value & 0xff;

    