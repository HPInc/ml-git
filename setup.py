"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from setuptools import setup
import mlgit

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

install_requirements = [
    "boto3==1.9.164",
    "GitPython==3.1.0",
    "PyYAML==5.1.1",
    "py-cid==0.2.1",
    "py-multihash==0.2.3",
    "botocore==1.12.172",
    "colorama==0.4.1",
    "tqdm==4.31.1",
    "click==7.0",
    "click-didyoumean==0.0.3",
    "click-plugins==1.1.1",
    "hurry.filesize==0.9",
    "azure-core==1.3.0",
    "azure-storage-blob==12.0.0",
    "toml==0.10.0"
]

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
    package_dir={'': '.'},
    packages=['mlgit', 'mlgit.commands'],
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
