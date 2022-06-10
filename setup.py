"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json
import sys
from pathlib import Path

from setuptools import setup, find_packages

from ml_git.version import get_version

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

this_directory = Path(__file__).parent
long_description = (this_directory/"README.md").read_text()

setup(
    name='ml-git',
    version=get_version(),
    url='https://github.com/HPInc/ml-git',
    project_urls={
        'Bug Tracker': 'https://github.com/HPInc/ml-git/issues',
    },
    license='GNU General Public License v2.0',
    author='Sebastien Tandel',
    description='ML-Git: version control for ML artefacts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    test_suite='tests',
    package_dir={'': '.'},
    packages=find_packages(),
    keywords='version control, cloud storage, machine learning, datasets, labels, models',
    platforms='Any',
    zip_safe=True,
    package_data={'ml_git': ['version.info']},
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
