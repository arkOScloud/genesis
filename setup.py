#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='genesis',
    version='0.6.3',
    install_requires=[
        'pyOpenSSL',
        'gevent',
        'lxml>=2.2.4',
    ],
    description='The server administration panel',
    author='Eugeny Pankov',
    author_email='e@genesis.org',
    url='http://genesis.org/',
    packages = find_packages(),
    package_data={'': ['files/*.*', 'files/*/*.*', 'files/*/*/*.*', 'templates/*.*', 'widgets/*.*', 'layout/*.*']},
    scripts=['genesis-panel', 'genesis-pkg'],
    data_files=[
        ('/etc/genesis', ['packaging/files/genesis.conf']),
        ('/etc/genesis/users', ['packaging/files/admin.conf']),
        ('/etc/init.d', ['packaging/files/genesis']),
        ('/var/lib/genesis/plugins', ['packaging/files/.placeholder']),
    ],
)
