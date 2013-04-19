#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='genesis',
    version='0.1',
    install_requires=[
        'pyOpenSSL',
        'gevent',
        'lxml>=2.2.4',
    ],
    description='arkOS node management app',
    author='Jacob Cook',
    author_email='jacob@jcook.cc',
    url='http://ark-os.org/',
    packages = find_packages(),
    package_data={'': ['files/*.*', 'files/*/*.*', 'files/*/*/*.*', 'templates/*.*', 'widgets/*.*', 'layout/*.*']},
    scripts=['genesis-panel', 'genesis-pkg'],
    data_files=[
        ('/etc/genesis', ['packaging/files/genesis.conf']),
        ('/etc/genesis/users', ['packaging/files/admin.conf']),
        ('/usr/lib/systemd/system', ['packaging/files/genesis.service']),
        ('/var/lib/genesis/plugins', ['packaging/files/.placeholder']),
    ],
)
