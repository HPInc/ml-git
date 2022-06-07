"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from click_didyoumean import DYMGroup

from ml_git import admin
from ml_git.commands import prompt_msg
from ml_git.commands.prompt_msg import CREDENTIALS_PROFILE_MESSAGE, REGION_MESSAGE, ENDPOINT_MESSAGE, \
    CREDENTIALS_PATH_MESSAGE, USERNAME_SFTPH, PRIVATE_KEY_SFTPH, SFTPH_ENDPOINT_MESSAGE
from ml_git.commands.repository import repository
from ml_git.commands.wizard import wizard_for_field, choise_wizard_for_field
from ml_git.constants import MultihashStorageType, StorageType



@repository.group('storage', help='Storage management for this ml-git repository.', cls=DYMGroup)
def storage():
    """
    Storage management for this ml-git repository.
    """
    pass


def storage_add(context, **kwargs):
    kwargs['type'] = choise_wizard_for_field(context, kwargs['type'], prompt_msg.STORAGE_TYPE_MESSAGE, click.Choice(MultihashStorageType.to_list()), default=StorageType.S3H.value)
    if kwargs['type'] == StorageType.S3H.value:
        admin.storage_add(kwargs['type'], kwargs['bucket_name'], wizard_for_field(context, kwargs['credentials'], CREDENTIALS_PROFILE_MESSAGE),
                          global_conf=kwargs['global'], endpoint_url=wizard_for_field(context, kwargs['endpoint_url'], ENDPOINT_MESSAGE),
                          region=wizard_for_field(context, kwargs['region'], REGION_MESSAGE))
    elif kwargs['type'] == StorageType.GDRIVEH.value:
        admin.storage_add(kwargs['type'], kwargs['bucket_name'],
                          wizard_for_field(context, kwargs['credentials'], CREDENTIALS_PATH_MESSAGE), global_conf=kwargs['global'])
    elif kwargs['type'] == StorageType.SFTPH.value:
        sftp_configs = {'username':  wizard_for_field(context, kwargs['username'], USERNAME_SFTPH),
                        'private_key':  wizard_for_field(context, kwargs['private_key'], PRIVATE_KEY_SFTPH),
                        'port': kwargs['port']}
        admin.storage_add(kwargs['type'], kwargs['bucket_name'], kwargs['credentials'],
                          global_conf=kwargs['global'], endpoint_url=wizard_for_field(context, kwargs['endpoint_url'], SFTPH_ENDPOINT_MESSAGE),
                          sftp_configs=sftp_configs)
    else:
        admin.storage_add(kwargs['type'], kwargs['bucket_name'], kwargs['credentials'], global_conf=kwargs['global'])


def storage_del(context, **kwargs):
    admin.storage_del(kwargs['type'], kwargs['bucket_name'], kwargs['global'])
