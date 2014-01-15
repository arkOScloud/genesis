import bz2
import gzip
import os
import tarfile
import zipfile

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
