#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='genesis',
    version='0.6.2',
    install_requires=[
        'pyOpenSSL',
        'gevent',
        'lxml>=2.2.4',
        'python-iptables',
        'python-nginx',
    ],
    description='arkOS node management app',
    author='The CitizenWeb Project',
    author_email='jacob@citizenweb.is',
    url='http://arkos.io/',
    packages=find_packages(),
    package_data={'': ['files/*.*', 'files/*/*.*', 'files/*/*/*.*', 'templates/*.*', 'widgets/*.*', 'layout/*.*']},
    scripts=['genesis-panel', 'genesis-pkg'],
    data_files=[
        ('/etc/genesis', ['packaging/files/genesis.conf']),
        ('/etc/genesis/users', ['packaging/files/admin.conf']),
        ('/usr/lib/systemd/system', ['packaging/files/genesis.service']),
        ('/var/lib/genesis/plugins', ['packaging/files/.placeholder']),
    ],
)
