"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from click_didyoumean import DYMGroup

import ml_git.admin as admin
from ml_git.commands.repository import repository
from ml_git.commands.utils import set_verbose_mode


@repository.group('store', help='Store management for this ml-git repository.', cls=DYMGroup)
def store():
    """
    Store management for this ml-git repository.
    """
    pass


@store.command('add', help='Add a store BUCKET_NAME to ml-git')
@click.argument('bucket-name')
@click.option('--credentials', default='default', help='Profile name for store credentials [default: default]')
@click.option('--region', default='us-east-1', help='Aws region name for S3 bucket [default: us-east-1]')
@click.option('--type', default='s3h', type=click.Choice(['s3h', 's3', 'azureblobh', 'gdriveh'], case_sensitive=True),
              help='Store type (s3h, s3, azureblobh, gdriveh ...) [default: s3h]')
@click.help_option(hidden=True)
@click.option('--endpoint-url', help='Store endpoint url')
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def store_add(**kwargs):
    admin.store_add(kwargs['type'], kwargs['bucket_name'], kwargs['credentials'], kwargs['endpoint_url'])


@store.command('del', help='Delete a store BUCKET_NAME from ml-git')
@click.argument('bucket-name')
@click.option('--type', default='s3h', type=click.Choice(['s3h', 's3', 'azureblobh', 'gdriveh'], case_sensitive=True),
              help='Store type (s3h, s3, azureblobh, gdriveh ...) [default: s3h]')
@click.help_option(hidden=True)
@click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode, help='Debug mode')
def store_del(**kwargs):
    admin.store_del(kwargs['type'], kwargs['bucket_name'])
