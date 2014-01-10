import os
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

    def init(self):
        self.ram = self.app.get_backend(apis.sysstat.ISysStat).get_ram()

    def get_max(self):
        return int(self.ram[1])

    def get_value(self):
        return int(self.ram[0])


class SwapMeter (LinearMeter):
    name = 'Swap'
    category = 'System'
    transform = 'fsize_percent'

    def init(self):
        self.swap = self.app.get_backend(apis.sysstat.ISysStat).get_swap()

    def get_max(self):
        return int(self.swap[1])

    def get_value(self):
        return int(self.swap[0])


class DiskUsageMeter(LinearMeter):
    name = 'Disk usage'
    category = 'System'
    transform = 'percent'

    _platform = detect_platform()
    _partstatformat = re.compile('(/dev/)?(?P<dev>\w+)\s+\d+\s+\d+\s+\d+\s+' +
                                       '(?P<usage>\d+)%\s+(?P<mountpoint>\S+)$')
    if 'arkos' in _platform or 'arch' in _platform:
        _totalformat = re.compile('(?P<dev>total)\s+\d+\s+\d+\s+\d+\s+(?P<usage>\d+)%+\s+\-$')
    else:
        _totalformat = re.compile('(?P<dev>total)\s+\d+\s+\d+\s+\d+\s+(?P<usage>\d+)%$')

    def init(self):
        if self.variant == 'total':
            self.text = 'total'
        else:
            mountpoints = self.get_mountpoints()
            self.text = '%s (%s)' % (self.variant, ', '.join(mountpoints))

    def _get_stats(self, predicate = (lambda m: True)):
        if hasattr(self, 'variant') and self.variant == 'total':
            matcher = DiskUsageMeter._totalformat
        else:
            matcher = DiskUsageMeter._partstatformat

        stats = shell('df --total')
        matches = []
        for stat in stats.splitlines():
            match = matcher.match(stat)
            if match and predicate(match):
                matches.append(match)
        return matches

    def _get_stats_for_this_device(self):
        return self._get_stats(lambda m: m.group('dev').endswith(self.variant))

    def get_variants(self):
        if 'arkos' in self._platform or 'arch' in self._platform:
            return sorted(set([ m.group('dev') for m in self._get_stats()]))
        else:
            return sorted(set([ m.group('dev') for m in self._get_stats()])) + ['total']

    def get_mountpoints(self):
        devmatches = self._get_stats_for_this_device()
        return sorted([ m.group('mountpoint') for m in devmatches])

    def get_value(self):
        devmatches = self._get_stats_for_this_device()
        return int(devmatches[0].group('usage'))

    def get_min(self):
        return 0

    def get_max(self):
        return 100


class CpuMeter(LinearMeter):
    name = 'CPU usage'
    category = 'System'
    transform = 'percent'
    
    def get_usage(self):
         u = shell('ps h -eo pcpu').split()
         b=0.0
         for a in u:  
            b += float(a)
         return b
    
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
        