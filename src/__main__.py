"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python

import click

from operations.add import handle_add_operation
from operations.config import handle_config_operation
from operations.init import handle_init_operation
from operations.push import handle_push_operation
from operations.status import handle_status_operation
from storage import StorageType
from utils import constants


@click.group()
def cli():
    pass


@cli.command(help='Initialize a ML repository')
@click.argument('dataset_source', required=False)
@click.option('--name', help='Project name', required=False, default=constants.DEFAULT_PROJECT_NAME)
@click.option('--version', help='Project version', required=False, default=constants.DEFAULT_PROJECT_VERSION)
@click.option('--label', help='Project labels', required=False, multiple=True, default=[])
@click.option('--storage-type', help='Data storage option', required=False, default='',
              type=click.Choice([''] + StorageType.StorageType.list()))
def init(dataset_source, name, version, label, storage_type):
    handle_init_operation(dataset_source, name, version, label, storage_type)


@cli.command(help='Configure ML-git')
@click.option('--storage-type', help='Data storage option', required=False, default='',
              type=click.Choice([''] + StorageType.StorageType.list()))
@click.option('--s3-credentials-path', help='AWS S3 bucket', required=False)
@click.option('--s3-bucket', help='AWS S3 bucket', required=False)
@click.option('--s3-region', help='AWS S3 region', required=False)
@click.option('--s3-access-key', help='AWS S3 accessKey', required=False)
@click.option('--s3-secret-key', help='AWS S3 secretKey', required=False)
def config(storage_type, s3_credentials_path, s3_bucket, s3_region, s3_access_key, s3_secret_key):
    handle_config_operation(storage_type, s3_credentials_path, s3_bucket, s3_region, s3_access_key, s3_secret_key)


@cli.command(help='Add a file to be tracked')
@click.argument('path', required=False)
def add(path):
    handle_add_operation(path)


@cli.command(help='Show status of tracked, new and modified files')
@click.argument('files', required=False, nargs=-1)
def status(files):
    handle_status_operation(files)


@cli.command(help='Upload the data set files and push the file to the remote repository')
def push():
    handle_push_operation()


@cli.command(help='Checkout to a specific tag or data set version')
@click.argument('tag', required=False)
@click.option('--category', help='fully qualified tag name', required=False)
@click.option('--name', help='fully qualified tag name', required=False)
@click.option('--version', help='fully qualified tag name', required=False)
def checkout(tag, category, name, version):
    click.secho(f'Checkout tag: {tag} category: {category} name: {name} version: {version}', fg='red', bold=True)


def main():
    try:
        cli()
    except Exception as e:
        click.secho(str(e), fg='red')


if __name__ == "__main__":
    main()
