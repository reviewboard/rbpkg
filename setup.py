#!/usr/bin/env python

from __future__ import unicode_literals

import sys

from setuptools import setup, find_packages

from rbpkg import get_package_version


PACKAGE_NAME = 'rbpkg'

install_requires = [
    'pip>=7.1.2',
    'python-dateutil',
    'six>=1.8.0',
]

if sys.hexversion < 0x02060000:
    sys.stderr.write('rbpkg requires Python 2.6 or 2.7.\n')
    sys.exit(1)
elif sys.hexversion < 0x02070000:
    install_requires.append('argparse')


rbpkg_commands = [
    'install = rbpkg.commands.install:InstallCommand',
    'upgrade = rbpkg.commands.upgrade:UpgradeCommand',
]


setup(
    name=PACKAGE_NAME,
    version=get_package_version(),
    license='MIT',
    description='Package installer for Review Board and friends.',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'rbpkg = rbpkg.commands.main:main',
        ],
        'rbpkg_commands': rbpkg_commands,
    },
    install_requires=install_requires,
    include_package_data=True,
    maintainer='Christian Hammond',
    maintainer_email='christian@beanbaginc.com',
    url='https://www.reviewboard.org/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
