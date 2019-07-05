"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ml-git",
    version="0.0.1",
    packages=find_packages('src'),
    package_dir={'':'src'},

    entry_points={
        'console_scripts': [
            'ml-git = main.__main__:main'
        ]
    },
    install_requires=['click', 'boto3', 'colorama', 'pyyaml', 'gitpython']
)
