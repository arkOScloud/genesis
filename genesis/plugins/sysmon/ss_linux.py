# -*- coding: UTF-8 -*-

import re
import os

from genesis import apis
from genesis.utils import shell, detect_architecture
from genesis.com import *


class LinuxSysStat(Plugin):
    implements(apis.sysstat.ISysStat)
    platform = ['debian', 'arch', 'arkos', 'centos', 'fedora', 'gentoo', 'mandriva']

    def get_load(self):
        return open('/proc/loadavg', 'r').read().split()[0:3]

    def get_temp(self):
        if self.app.board == 'Raspberry Pi':
            return '%3.1f°C'%(float(shell('cat /sys/class/thermal/thermal_zone0/temp').split('\n')[0])/1000)
        else:
            if os.path.exists('/sys/class/hwmon/hwmon1/temp1_input'):
                return '%3.1f°C'%(float(shell('cat /sys/class/hwmon/hwmon1/temp1_input'))/1000)
        return ''

    def get_ram(self):
        s = shell('free -b | grep Mem').split()[1:]
        t = int(s[0])
        u = int(s[1])
        b = int(s[4])
        c = int(s[5])
        u -= c + b;
        return (u, t)

    def get_swap(self):
        s = shell('free -b | grep Swap').split()[1:]
        return (int(s[1]), int(s[0]))

    def get_uptime(self):
        minute = 60
        hour = minute * 60
        day = hour * 24

        d = h = m = 0

        try:
            s = int(open('/proc/uptime').read().split('.')[0])

            d = s / day
            s -= d * day
            h = s / hour
            s -= h * hour
            m = s / minute
            s -= m * minute
        except IOError:
            # Try use 'uptime' command
            up = os.popen('uptime').read()
            if up:
                uptime = re.search('up\s+(.*?),\s+[0-9]+ user',up).group(1)
                return uptime

        uptime = ""
        if d > 1:
            uptime = "%d days, "%d
        elif d == 1:
            uptime = "1 day, "

        return uptime + "%d:%02d:%02d"%(h,m,s)
