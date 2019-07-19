"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from setuptools import setup
from src import mlgit

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

install_requirements = parse_requirements("requirements.txt")

setup_requirements = []
test_requirements = []

setup(
    name='ml-git',
    version=mlgit.__version__,
    url='',
    license='GNU General Public License v2.0',
    author="Sébastien Tandel",
    description='ml-git: version control for ML artefacts',
    long_description='ml-git: a Distributed Version Control for ML artefacts',
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    test_suite="tests",
    package_dir={'': 'src'},
    packages=['mlgit'],
    keywords='version control, cloud storage, machine learning, datasets, labels, models',
    platforms='Any',
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],entry_points={
        'console_scripts': [
            'ml-git = mlgit.main:run_main',
        ],
    },
)
