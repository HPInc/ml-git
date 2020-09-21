"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pprint import pprint

import click

from ml_git.admin import init_mlgit
from ml_git.commands.general import mlgit
from ml_git.config import config_load, global_config_load, mlgit_config_load
from click_didyoumean import DYMGroup


@mlgit.group('repository', help='Management of this ml-git repository.', cls=DYMGroup)
def repository():
    """
    Management of this ml-git repository.
    """
    pass


@repository.command('init', help='Initialiation of this ml-git repository')
def init():
    init_mlgit()


@repository.command('config', help='Configuration of this ml-git repository')
@click.option('--local', '-l', is_flag=True, default=False, help='Local configurations')
@click.option('--global', '-g', is_flag=True, default=False, help='Global configurations')
def config(**kwargs):
    config_file = config_load()
    if kwargs['global']:
        config_file = global_config_load()
    elif kwargs['local']:
        config_file = mlgit_config_load()
    print('config:')
    pprint(config_file)
