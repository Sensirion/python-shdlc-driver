# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from setuptools import setup, find_packages
import os
import re


# Read version number from version.py
version_line = open("sensirion_shdlc_driver/version.py", "rt").read()
result = re.search(r"^version = ['\"]([^'\"]*)['\"]", version_line, re.M)
if result:
    version_string = result.group(1)
else:
    raise RuntimeError("Unable to find version string")


# Use README.rst and CHANGELOG.rst as package description
root_path = os.path.dirname(__file__)
readme = open(os.path.join(root_path, 'README.rst')).read()
changelog = open(os.path.join(root_path, 'CHANGELOG.rst')).read()
long_description = readme.strip() + "\n\n" + changelog.strip() + "\n"


setup(
    name='sensirion-shdlc-driver',
    version=version_string,
    author='Urban Bruhin',
    author_email='urban.bruhin@sensirion.com',
    description='Base Driver for Communicating With Sensirion SHDLC Devices',
    license='BSD',
    keywords='shdlc sensirion sensor driver',
    url='https://github.com/sensirion/python-shdlc-driver',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    setup_requires=[
        'pytest-runner~=4.2',
    ],
    install_requires=[
        'pyserial~=3.0',
    ],
    extras_require={
        # Dependencies for the firmware update (optional since not all devices
        # support firmware updates)
        'fwupdate': [
            'intelhex~=2.0',
        ],
        # Dependencies for tests
        'test': [
            'flake8~=3.6.0',
            'intelhex~=2.0',  # from the "fwupdate" extra
            'mock~=3.0.0',
            'pytest~=3.10.0',
            'pytest-cov~=2.6.0',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Hardware :: Hardware Drivers'
    ]
)
