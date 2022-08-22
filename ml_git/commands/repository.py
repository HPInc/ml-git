"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pprint import pprint

import click
from click import UsageError
from click_didyoumean import DYMGroup

from ml_git import api
from ml_git.admin import init_mlgit
from ml_git.commands import help_msg
from ml_git.commands.custom_options import MutuallyExclusiveOption
from ml_git.commands.custom_types import NotEmptyString
from ml_git.commands.general import mlgit
from ml_git.commands.utils import repositories, PROJECT, set_verbose_mode
from ml_git.commands.wizard import WizardMode, change_wizard_mode
from ml_git.config import global_config_load, mlgit_config_load, merged_config_load


@mlgit.group('repository', help='Management of this ml-git repository.', cls=DYMGroup)
def repository():
    """
    Management of this ml-git repository.
    """
    pass


@repository.group('config', help='Management of the ML-Git config file.', cls=DYMGroup, invoke_without_command=True)
@click.option('--set-wizard', help=help_msg.WIZARD_MODE, type=click.Choice(WizardMode.to_list(), case_sensitive=True))
@click.pass_context
def config(ctx, set_wizard):
    """
    Management of the ML-Git config file.
    """
    if set_wizard:
        change_wizard_mode(set_wizard)
    elif ctx.invoked_subcommand is None:
        raise UsageError('Missing command')


@repository.command('init', help='Initialization of this ML-Git repository')
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


@repository.command('update', help='This command will update all ml-entities\' metadata repository.')
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


@repository.command('graph', help='Creates a graph of all entity relations as an HTML file'
                                  ' and automatically displays it in the default system application.')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
@click.option('--dot', is_flag=True, default=False, help='Instead of creating an HTML file,'
                                                         ' it displays the graph on the command line as a DOT language.')
@click.option('--export-path', type=NotEmptyString(), help='Set the directory path to export the generated graph file.')
def graph(dot, export_path):
    local_entity_manager = api.init_local_entity_manager()
    local_entity_manager.display_graph(export_path, dot)
