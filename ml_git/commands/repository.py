"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pprint import pprint

from ml_git.admin import init_mlgit
from ml_git.commands.general import mlgit
from ml_git.config import config_load
from click_didyoumean import DYMGroup


@mlgit.group('repository', help='Management of this ml-git repository', cls=DYMGroup)
def repository():
    pass


@repository.command('init', help='Initialiation of this ml-git repository')
def init():
    init_mlgit()


@repository.command('config', help='Configuration of this ml-git repository')
def config():
    config_file = config_load()
    print('config:')
    pprint(config_file)
