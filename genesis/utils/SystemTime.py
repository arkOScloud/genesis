import ntplib
import time

from utils import shell_cs


def get_datetime(display=''):
    if display:
        return time.strftime(display)
    else:
        return time.localtime()

def get_idatetime():
    ntp = ntplib.NTPClient()
    resp = ntp.request('0.pool.ntp.org', version=3)
    return resp.tx_time

def set_datetime(dt=''):
    dt = dt if dt else get_idatetime()
    e = shell_cs('date -s @%s' % dt)
    if e[0] != 0:
        raise Exception('System time could not be set. Error: %s' % str(e[1]))

def convert(intime, infmt, outfmt):
    return time.strftime(outfmt, time.strptime(intime, infmt))

def get_serial_time():
    return time.strftime('%Y%m%d%H%M%S')

def get_date():
    return time.strftime('%d %b %Y')

def get_time():
    return time.strftime('%H:%M')

def get_offset():
    ntp = ntplib.NTPClient()
    resp = ntp.request('0.pool.ntp.org', version=3)
    return resp.offset
