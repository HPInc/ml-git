"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click

from pkg_resources import iter_entry_points
from mlgit.commands.utils import repositories, PROJECT
from mlgit import __version__
from click_didyoumean import DYMGroup
from click_plugins import with_plugins


@with_plugins(iter_entry_points('mlgit.plugins'))
@click.group(cls=DYMGroup)
@click.version_option(version=__version__,  message='%(prog)s %(version)s')
@click.help_option(hidden=True)
def mlgit():
    pass


# Concrete ml-git Commands Implementation
@mlgit.command('clone', help='Clone a ml-git repository ML_GIT_REPOSITORY_URL')
@click.argument('repository_url')
@click.option('--folder', default=None, help='The configuration files are cloned in specified folder.')
@click.option('--track', is_flag=True, default=False, help='Preserves .git folder in the same directory '
                                                           'of cloned configuration files.')
@click.help_option(hidden=True)
def clone(**kwargs):
    repositories[PROJECT].clone_config(kwargs['repository_url'], kwargs['folder'], kwargs['track'])
