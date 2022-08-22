"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
import click_completion
from click_didyoumean import DYMGroup
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from ml_git.commands.utils import repositories, PROJECT, set_verbose_mode
from ml_git.utils import check_metadata_directories
from ml_git.version import get_version


click_completion.init()


@with_plugins(iter_entry_points('mlgit.plugins'))
@click.group(cls=DYMGroup)
@click.version_option(version=get_version(),  message='%(prog)s %(version)s')
@click.help_option(hidden=True)
def mlgit():
    check_metadata_directories()


@mlgit.command('clone', help='Clone an ml-git repository ML_GIT_REPOSITORY_URL')
@click.argument('repository_url')
@click.argument('directory', required=False)
@click.option('--untracked', is_flag=True, default=False, help='Does not preserve git repository tracking.')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def clone(**kwargs):
    repositories[PROJECT].clone_config(kwargs['repository_url'], kwargs['directory'], kwargs['untracked'])
