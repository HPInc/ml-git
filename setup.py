"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json
import sys

from setuptools import setup, find_packages
import ml_git


try:
    with open('Pipfile.lock') as fd:
        lock_data = json.load(fd)
        install_requires = [
            package_name + package_data.get('version', '')
            for package_name, package_data in lock_data['default'].items()
        ]
        tests_require = [
            package_name + package_data.get('version', '')
            for package_name, package_data in lock_data['develop'].items()
        ]
except FileNotFoundError:
    print('File Pipfile.lock not found. Run `pipenv lock` to generate it.')
    sys.exit(1)


install_requirements = install_requires

setup_requirements = []
test_requirements = tests_require

setup(
    name='ml-git',
    version=ml_git.__version__,
    url='https://git@github.com/ml-git',
    license='GNU General Public License v2.0',
    author="Sébastien Tandel",
    description='ml-git: version control for ML artefacts',
    long_description='ml-git: a Distributed Version Control for ML artefacts',
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    test_suite="tests",
    package_dir={'': '.'},
    packages=find_packages(),
    keywords='version control, cloud storage, machine learning, datasets, labels, models',
    platforms='Any',
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ], entry_points={
        'console_scripts': [
            'ml-git = ml_git.main:run_main',
        ],
    },
)
