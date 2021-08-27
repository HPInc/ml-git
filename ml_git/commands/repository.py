"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pprint import pprint

import click
from click_didyoumean import DYMGroup

from ml_git import api
from ml_git.admin import init_mlgit
from ml_git.commands import help_msg
from ml_git.commands.custom_options import MutuallyExclusiveOption
from ml_git.commands.general import mlgit
from ml_git.commands.utils import repositories, PROJECT, set_verbose_mode
from ml_git.config import global_config_load, mlgit_config_load, merged_config_load
from ml_git.constants import FileType


@mlgit.group('repository', help='Management of this ml-git repository.', cls=DYMGroup)
def repository():
    """
    Management of this ml-git repository.
    """
    pass


@repository.group('config', help='Management of the ML-Git config file.', cls=DYMGroup)
def config():
    """
    Management of the ML-Git config file.
    """
    pass


@repository.command('init', help='Initialiation of this ml-git repository')
def init():
    init_mlgit()


@config.command('show', help='Configuration of this ML-Git repository')
@click.option('--local', '-l', is_flag=True, default=False, help=help_msg.LOCAL_CONFIGURATIONS,
              cls=MutuallyExclusiveOption, mutually_exclusive=['global'])
@click.option('--global', '-g', is_flag=True, default=False, help=help_msg.GLOBAL_CONFIGURATIONS,
              cls=MutuallyExclusiveOption, mutually_exclusive=['local'])
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help=help_msg.VERBOSE_OPTION)
@click.help_option(hidden=True)
def show(**kwargs):
    if kwargs['global']:
        config_file = global_config_load()
    elif kwargs['local']:
        config_file = mlgit_config_load()
    else:
        config_file = merged_config_load()

    print('config:')
    pprint(config_file)


@repository.command('update', help='This command will update all ml-entities metadata repository.')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def update():
    repositories[PROJECT].update_entities_metadata()


@repository.command('gc', help='Cleanup unnecessary files and optimize the use of the disk space.')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def gc():
    repositories[PROJECT].garbage_collector()


@config.command('push', help='Create a new version of the ML-Git configuration file. '
                             'This command internally runs git\'s add, commit and push commands.')
@click.option('--message', '-m', default='Updating config file', help='Use the provided <msg> as the commit message.')
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
@click.help_option(hidden=True)
def push(**kwargs):
    repositories[PROJECT].repo_config_push(kwargs['message'])
    pass


@repository.command('graph', help='Create a graph of all entities relationships as DOT language')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def graph():
    local_entity_manager = api.init_local_entity_manager()
    print(local_entity_manager.get_project_entities_relationships(export_type=FileType.DOT.value))
