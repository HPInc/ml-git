"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from click_didyoumean import DYMGroup

from ml_git.commands.repository import repository
from ml_git.commands.utils import LABELS, repositories, set_verbose_mode, DATASETS, MODELS, PROJECT


@repository.group('remote', help='Configure remote ml-git metadata repositories.', cls=DYMGroup)
def repo_remote():
    """
    Configure remote ml-git metadata repositories.
    """
    pass


@repo_remote.group(DATASETS, help='Manage remote ml-git datasets metadata repository.', cls=DYMGroup)
@click.pass_context
def repo_remote_ds(ctx):
    """
    Manage remote ml-git dataset metadata repository.
    """
    pass


@repo_remote.group(LABELS, help='Manage remote ml-git labels metadata repository.', cls=DYMGroup)
def repo_remote_lb():
    """
    Manage remote ml-git labels metadata repository.
    """
    pass


@repo_remote.group(MODELS, help='Manage remote ml-git models metadata repository.', cls=DYMGroup)
@click.pass_context
def repo_remote_md(ctx):
    """
    Manage remote ml-git model metadata repository.
    """
    pass


@repo_remote_ds.command('add', help='Add remote dataset metadata REMOTE_URL to this ml-git repository')
@click.argument('remote-url')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
@click.help_option(hidden=True)
def repo_remote_ds_add(**kwargs):
    repositories[DATASETS].repo_remote_add(DATASETS, kwargs['remote_url'], kwargs['global'])


@repo_remote_lb.command('add', help='Add remote labels metadata REMOTE_URL to this ml-git repository')
@click.argument('remote-url')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
@click.help_option(hidden=True)
def repo_remote_lb_add(**kwargs):
    repositories[LABELS].repo_remote_add(LABELS, kwargs['remote_url'], kwargs['global'])


@repo_remote_md.command('add', help='add remote model metadata REMOTE_URL to this ml-git repository')
@click.argument('remote-url')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
@click.help_option(hidden=True)
def repo_remote_md_add(**kwargs):
    repositories[MODELS].repo_remote_add(MODELS, kwargs['remote_url'], kwargs['global'])


@repo_remote_ds.command('del', help='Remove remote datasets metadata REMOTE_URL from this ml-git repository')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def repo_remote_ds_del(**kwargs):
    repositories[DATASETS].repo_remote_del(kwargs['global'])


@repo_remote_lb.command('del', help='Remove remote labels metadata REMOTE_URL from this ml-git repository')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def repo_remote_lb_del(**kwargs):
    repositories[LABELS].repo_remote_del(kwargs['global'])


@repo_remote_md.command('del', help='Remove remote model metadata REMOTE_URL from this ml-git repository')
@click.option('--global', '-g', is_flag=True, default=False, help='Use this option to set configuration at global level')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def repo_remote_md_del(**kwargs):
    repositories[MODELS].repo_remote_del(kwargs['global'])


@repo_remote.group('config', help='Manage remote ML-Git config repository.', cls=DYMGroup)
@click.pass_context
def repo_remote_config(ctx):
    """
    Manage remote ML-Git config repository.
    """
    pass


@repo_remote_config.command('add', help='Starts a git at the root of the project and configure the remote.')
@click.argument('remote-url')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def repo_remote_config_add(**kwargs):
    repositories[PROJECT].repo_config_init(kwargs['remote_url'])
