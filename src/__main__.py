"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python

import click

from operations.init import handle_init_operation
from operations.status import handle_status_operation
from utils.constants import *


@click.group()
def cli():
    pass


@cli.command(help='Initialize a ML repository')
@click.argument('dataset_source', required=False)
@click.option('--name', help='Project name', required=False, default=DEFAULT_PROJECT_NAME)
@click.option('--version', help='Project version', required=False, default=DEFAULT_PROJECT_VERSION)
@click.option('--label', help='Project labels', required=False, multiple=True, default=[])
@click.option('--data-store', help='Data storage option', required=False, default='')
def init(dataset_source, name, version, label, data_store):
    handle_init_operation(dataset_source, name, version, label, data_store)


@cli.command(help='Add a file to be tracked')
@click.argument('file')
def add(file):
    click.echo(f'Add {file}')


@cli.command(help='Add a file to be tracked')
@click.argument('files', required=False, nargs=-1)
def status(files):
    handle_status_operation(files)


@cli.command(help='Upload the data set files and push the file to the remote repository')
def push():
    click.echo('Push')


@cli.command(help='Checkout to a specific tag or data set version')
@click.argument('tag', required=False)
@click.option('--category', help='fully qualified tag name', required=False)
@click.option('--name', help='fully qualified tag name', required=False)
@click.option('--version', help='fully qualified tag name', required=False)
def checkout(tag, category, name, version):
    click.secho(f'Checkout tag: {tag} category: {category} name: {name} version: {version}', fg='red', bold=True)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        click.echo(e, color='red')
