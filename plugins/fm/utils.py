import bz2
import gzip
import os
import tarfile
import tempfile
import zipfile


def compress(pin, pout='', format='tgz', delete=False):
    if format == 'tgz':
        pout = tempfile.mkstemp('.tar.gz')[1] if not pout else pout
        a = tarfile.open(pout, 'w:gz')
        for x in pin:
            a.add(x, os.path.split(x)[1])
        a.close()
    elif format == 'zip':
        pout = tempfile.mkstemp('.zip')[1] if not pout else pout
        a = zipfile.ZipFile(pout, 'w')
        for x in pin:
            a.write(x)
        a.close()
    return pout

def extract(pin, pout, delete=False):
    name = os.path.basename(pin)
    if name.endswith(('.tar.gz', '.tgz')):
        t = tarfile.open(pin, 'r:gz')
        t.extractall(pout)
    elif name.endswith('.gz'):
        i = gzip.open(pin, 'rb').read()
        open(os.path.join(pout, name.split('.gz')[0]), 'wb').write(i)
    elif name.endswith(('.tar.bz2', '.tbz2')):
        t = tarfile.open(pin, 'r:bz2')
        t.extractall(f[0])
    elif name.endswith('.bz2'):
        i = bz2.BZ2File(pin, 'r').read()
        open(os.path.join(pout, name.split('.bz2')[0]), 'wb').write(i)
    elif name.endswith('.zip'):
        zipfile.ZipFile(pin, 'r').extractall(pout)
    else:
        raise Exception('Not an archive, or unknown archive type')
    if delete:
        os.unlink(pin)
