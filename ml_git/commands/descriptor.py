"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import copy

import click

from ml_git.commands import entity, help_msg
from ml_git.commands.custom_options import MutuallyExclusiveOption, OptionRequiredIf
from ml_git.commands.utils import set_verbose_mode

commands = [

    {
        'name': 'init',

        'callback': entity.init,
        'groups': [entity.dataset, entity.model, entity.labels],

        'help': 'Init a ml-git %s repository.'

    },

    {
        'name': 'list',

        'callback': entity.list_entity,
        'groups': [entity.dataset, entity.model, entity.labels],

        'help': 'List %s managed under this ml-git repository.'

    },

    {
        'name': 'fsck',

        'callback': entity.fsck,
        'groups': [entity.dataset, entity.model, entity.labels],

        'help': 'Perform fsck on %s in this ml-git repository.'

    },

    {
        'name': 'push',
        'callback': entity.push,
        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
            '--clearonfail': {'is_flag': True, 'help': help_msg.CLEAR_ON_FAIL},
        },

        'help': 'Push local commits from ML_ENTITY_NAME to remote ml-git repository & store.'

    },

    {
        'name': 'checkout',
        'callback': entity.checkout,
        'groups': [entity.dataset],

        'options': {
            '--sample-type': {'type': click.Choice(['group', 'range', 'random'])},
            '--sampling': {'default': '1:1000', 'help': help_msg.SAMPLING_OPTION},

            '--seed': {'default': '1', 'help': help_msg.SEED_OPTION},

            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

            '--force': {'default': False, 'is_flag': True, 'help': help_msg.FORCE_CHECKOUT},
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION}
        },

        'arguments': {
            'ml-entity-tag': {},

        },

        'help': 'Checkout the ML_ENTITY_TAG of a dataset into user workspace.'

    },

    {
        'name': 'checkout',
        'callback': entity.checkout,
        'groups': [entity.labels],

        'arguments': {
            'ml-entity-tag': {},

        },

        'options': {
            ('--with-dataset', '-d'): {'is_flag': True, 'default': False, 'help': help_msg.ASSOCIATED_WITH_DATASET},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

            '--force': {'is_flag': True, 'default': False, 'help': help_msg.FORCE_CHECKOUT},
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION}
        },

        'help': 'Checkout the ML_ENTITY_TAG of a label set into user workspace.'

    },

    {
        'name': 'checkout',
        'callback': entity.checkout,
        'groups': [entity.model],
        'options': {
            ('--with-labels', '-l'): {'is_flag': True, 'default': False, 'help': help_msg.ASSOCIATED_WITH_LABELS},
            ('--with-dataset', '-d'): {'is_flag': True, 'default': False, 'help': help_msg.ASSOCIATED_WITH_DATASET},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

            '--force': {'default': False, 'is_flag': True, 'help': help_msg.FORCE_CHECKOUT},
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION}
        },

        'arguments': {
            'ml-entity-tag': {},

        },

        'help': 'Checkout the ML_ENTITY_TAG of a model set into user workspace.'

    },

    {
        'name': 'fetch',
        'callback': entity.fetch,
        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-tag': {},

        },

        'options': {
            '--sample-type': {'type': click.Choice(['group', 'range', 'random'])},
            '--sampling': {'default': '1:1000',
                           'help': help_msg.SAMPLING_OPTION
                           },

            '--seed': {'default': '1', 'help': help_msg.SEED_OPTION},

            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
        },

        'help': 'Allows you to download just the metadata files of an entity.'

    },

    {
        'name': 'status',

        'callback': entity.status,
        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'Print the files that are tracked or not and the ones that are in the index/staging area.'

    },

    {
        'name': 'show',

        'callback': entity.show,
        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'Print the specification file of the entity.'

    },

    {
        'name': 'add',
        'callback': entity.add,
        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {},
            'file-path': {'nargs': -1, 'required': False}
        },

        'options': {
            '--bumpversion': {'is_flag': True, 'help': help_msg.BUMP_VERSION},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION}
        },

        'help': 'Add %s change set ML_ENTITY_NAME to the local ml-git staging area.'

    },

    {
        'name': 'commit',
        'callback': entity.commit,
        'groups': [entity.dataset],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version-number': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'help': help_msg.FSCK_OPTION},
        },

        'help': 'Commit dataset change set of ML_ENTITY_NAME locally to this ml-git repository.'

    },

    {
        'name': 'commit',
        'callback': entity.commit,
        'groups': [entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--dataset': {'help': 'Link dataset entity name to this label set version.'},
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version-number': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'help': help_msg.FSCK_OPTION},
        },

        'help': 'Commit labels change set of ML_ENTITY_NAME locally to this ml-git repository.'

    },

    {
        'name': 'commit',
        'callback': entity.commit,
        'groups': [entity.model],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--dataset': {'help': help_msg.LINK_DATASET},
            '--labels': {'help': help_msg.LINK_LABELS},
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version-number': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'help': help_msg.FSCK_OPTION},
        },

        'help': 'Commit model change set of ML_ENTITY_NAME locally to this ml-git repository.'

    },

    {
        'name': 'list',

        'callback': entity.tag_list,

        'groups': [entity.dt_tag_group, entity.lb_tag_group, entity.md_tag_group],

        'arguments': {
            'ml-entity-name': {},
        },

        'help': 'List tags of ML_ENTITY_NAME from this ml-git repository.'

    },

    {
        'name': 'add',

        'callback': entity.add_tag,

        'groups': [entity.dt_tag_group, entity.lb_tag_group, entity.md_tag_group],

        'arguments': {
            'ml-entity-name': {},
            'tag': {}
        },

        'help': 'Use this command to associate a tag to a commit.'

    },

    {
        'name': 'reset',

        'callback': entity.reset,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--hard': {'is_flag': True, 'default': False, 'help': help_msg.RESET_HARD},
            '--mixed': {'is_flag': True, 'default': False, 'help': help_msg.RESET_MIXED},
            '--soft': {'is_flag': True, 'default': False, 'help': help_msg.RESET_SOFT},
            '--reference': {'type': click.Choice(['head', 'head~1']),
                            'default': 'head', 'help': help_msg.RESET_REFENCE}
        },

        'help': 'Reset ml-git state(s) of an ML_ENTITY_NAME'

    },

    {
        'name': 'import',

        'callback': entity.import_tag,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'bucket-name': {'required': True},
            'entity-dir': {'required': True}
        },

        'options': {
            '--credentials': {'default': 'default',
                              'help': help_msg.CREDENTIALS_OPTION},
            '--region': {'default': 'us-east-1', 'help': help_msg.REGION_OPTION},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
            '--path': {'default': None, 'help': help_msg.PATH_OPTION},
            '--object': {'default': None, 'help': help_msg.OBJECT_OPTION},
            '--store-type': {'default': 's3', 'help': help_msg.STORE_TYPE,
                             'type': click.Choice(['s3', 'gdrive'])},
            '--endpoint-url': {'default': '', 'help': help_msg.ENDPOINT_URL},
        },

        'help': 'This command allows you to download a file or directory from the S3 or Gdrive to ENTITY_DIR.'

    },

    {
        'name': 'export',

        'callback': entity.export_tag,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml_entity_tag': {'required': True},
            'bucket-name': {'required': True}

        },

        'options': {
            '--credentials': {'default': 'default', 'help': help_msg.AWS_CREDENTIALS},
            '--endpoint': {'default': None, 'help': help_msg.ENDPOINT_URL},
            '--region': {'default': 'us-east-1', 'help': help_msg.REGION_OPTION},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

        },

        'help': 'This command allows you to export files from one store (S3|MinIO) to another (S3|MinIO).'

    },

    {
        'name': 'update',

        'callback': entity.update,

        'groups': [entity.dataset, entity.model, entity.labels],

        'help': 'This command will update the metadata repository.'

    },

    {
        'name': 'branch',

        'callback': entity.branch,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'This command allows to check which tag is checked out in the ml-git workspace.'

    },

    {
        'name': 'remote-fsck',

        'callback': entity.remote_fsck,

        'groups': [entity.dataset, entity.model, entity.labels],

        'options': {
            '--thorough': {'is_flag': True, 'help': help_msg.THOROUGH_OPTION},
            '--paranoid': {'is_flag': True, 'help': help_msg.PARANOID_OPTION},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
        },

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'This command will check and repair the remote by uploading lacking chunks/blobs.'

    },

    {
        'name': 'create',

        'callback': entity.create,

        'groups': [entity.dataset, entity.model, entity.labels],

        'options': {
            '--category': {'required': True, 'multiple': True, 'help': help_msg.CATEGORY_OPTION},
            '--store-type': {'type': click.Choice(['s3h', 'azureblobh', 'gdriveh']),
                             'help': help_msg.STORE_TYPE, 'default': 's3h'},
            '--version-number': {'help': help_msg.VERSION_NUMBER, 'default': 1},
            '--import': {'help': help_msg.IMPORT_OPTION,
                         'cls': MutuallyExclusiveOption, 'mutually_exclusive': ['import_url', 'credentials_path']},
            '--wizard-config': {'is_flag': True, 'help': help_msg.WIZARD_CONFIG},
            '--bucket-name': {'help': help_msg.BUCKET_NAME},
            '--import-url': {'help': help_msg.IMPORT_URL,
                             'cls': MutuallyExclusiveOption, 'mutually_exclusive': ['import']},
            '--credentials-path': {'default': None, 'help': help_msg.CREDENTIALS_PATH,
                                   'cls': OptionRequiredIf, 'required_option': ['import-url']},
            '--unzip': {'help': help_msg.UNZIP_OPTION, 'is_flag': True}
        },

        'arguments': {
            'artifact-name': {},
        },

        'help': 'This command will create the workspace structure with data and spec '
                'file for an entity and set the git and store configurations.'

    },

    {
        'name': 'unlock',

        'callback': entity.unlock,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {},
            'file': {},
        },

        'help': 'This command add read and write permissions to file or directory.'
                ' Note: You should only use this command for the flexible mutability option.'

    },
    {
        'name': 'log',

        'callback': entity.log,

        'groups': [entity.dataset, entity.model, entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--stat': {'is_flag': True, 'help': help_msg.STAT_OPTION, 'default': False},
            '--fullstat': {'is_flag': True, 'help': help_msg.FULL_STAT_OPTION, 'default': False},
        },

        'help': 'This command shows ml-entity-name\'s commit information like author, date, commit message.'

    }

]


def define_command(descriptor):
    callback = descriptor['callback']

    command = click.command(name=descriptor['name'], help=descriptor['help'])(click.pass_context(callback))

    if 'arguments' in descriptor:
        for key, value in descriptor['arguments'].items():
            command = click.argument(key, **value)(command)

    if 'options' in descriptor:
        for key, value in descriptor['options'].items():
            if type(key) == tuple:
                click_option = click.option(*key, **value)
            else:
                click_option = click.option(key, **value)
            command = click_option(command)

    command = click.help_option(hidden=True)(command)
    verbose_option = click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode,
                                  help='Debug mode')
    command = verbose_option(command)

    for group in descriptor['groups']:
        command_copy = copy.deepcopy(command)
        if '%s' in descriptor['help']:
            command_copy.help = descriptor['help'] % group.name
        group.add_command(command_copy)


for description in commands:
    define_command(description)
