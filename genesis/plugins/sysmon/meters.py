import os
import psutil
import re

from genesis.api import *
from genesis.utils import shell, detect_platform
from genesis import apis


class SysloadMeter (DecimalMeter):
    name = 'System load'
    category = 'System'
    transform = 'float'

    def get_variants(self):
        return ['1', '5', '15']

    def init(self):
        self.load = self.app.get_backend(apis.sysstat.ISysStat).get_load()
        self.text = self.variant + ' min'

    def get_value(self):
        return float(self.load[self.get_variants().index(self.variant)])


class RAMMeter (LinearMeter):
    name = 'RAM'
    category = 'System'
    transform = 'fsize_percent'

    def get_value(self):
        return psutil.virtual_memory().percent


class SwapMeter (LinearMeter):
    name = 'Swap'
    category = 'System'
    transform = 'fsize_percent'

    def get_value(self):
        return psutil.swap_memory().percent


class DiskUsageMeter(LinearMeter):
    name = 'Disk usage'
    category = 'System'
    transform = 'percent'

    def init(self):
        if self.variant == 'total':
            self.text = 'total'
        else:
            self.text = '%s (%s)' % (self.variant, next(x.mountpoint for x in psutil.disk_partitions() if x.device == self.variant))

    def get_variants(self):
        return [x.device for x in psutil.disk_partitions()] + ['total']

    def get_value(self):
        if self.variant == 'total':
            u, f, n = 0, 0, 0
            for x in psutil.disk_partitions():
                d = psutil.disk_usage(x.mountpoint)
                u += d.used
                f += d.free
                n += 1
            return ((float(u)/float(f))*100)/n
        else:
            return psutil.disk_usage(next(x.mountpoint for x in psutil.disk_partitions() if x.device == self.variant)).percent

    def get_min(self):
        return 0

    def get_max(self):
        return 100


class CpuMeter(LinearMeter):
    name = 'CPU usage'
    category = 'System'
    transform = 'percent'
    
    def get_usage(self):
        return psutil.cpu_percent()
    
    def get_value(self):
        return self.get_usage()
    
    def get_min(self):
        return 0
    
    def get_max(self):
        return 100


class ServiceMeter (BinaryMeter):
    name = 'Service'
    category = 'Software'
    transform = 'running'

    def get_variants(self):
        return [x.name for x in self.app.get_backend(apis.services.IServiceManager).list_all()]

    def init(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        self.text = self.variant

    def get_value(self):
        return self.mgr.get_status(self.variant) == 'running'
        