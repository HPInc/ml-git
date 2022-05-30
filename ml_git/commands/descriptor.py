"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
import copy

from ml_git.commands import entity, help_msg, storage, prompt_msg
from ml_git.commands.custom_options import MutuallyExclusiveOption, OptionRequiredIf, DeprecatedOptionsCommand
from ml_git.commands.custom_types import CategoriesType, NotEmptyString
from ml_git.commands.utils import set_verbose_mode
from ml_git.commands.wizard import WIZARD_ENABLE_KEY
from ml_git.config import merged_config_load
from ml_git.constants import MultihashStorageType, MutabilityType, StorageType, FileType

commands = [

    {
        'name': 'init',

        'callback': entity.init,
        'groups': [entity.datasets, entity.models, entity.labels],

        'help': 'Init a ml-git %s repository.'

    },

    {
        'name': 'list',

        'callback': entity.list_entity,
        'groups': [entity.datasets, entity.models, entity.labels],

        'help': 'List %s managed under this ml-git repository.'

    },

    {
        'name': 'fsck',

        'callback': entity.fsck,
        'groups': [entity.datasets, entity.models, entity.labels],

        'help': 'Perform fsck on %s in this ml-git repository.',

        'options': {
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.FSCK_FULL_OPTION},
        },


    },

    {
        'name': 'push',
        'callback': entity.push,
        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
            '--clearonfail': {'is_flag': True, 'help': help_msg.CLEAR_ON_FAIL},
            '--fail-limit': {'type': int, 'help': help_msg.FAIL_LIMIT}
        },

        'help': 'Push local commits from ML_ENTITY_NAME to remote ml-git repository & storage.'

    },

    {
        'name': 'checkout',
        'callback': entity.checkout,
        'groups': [entity.datasets],

        'options': {
            '--sample-type': {'type': click.Choice(['group', 'range', 'random'])},
            '--sampling': {'default': '1:1000', 'help': help_msg.SAMPLING_OPTION},

            '--seed': {'default': '1', 'help': help_msg.SEED_OPTION},

            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

            '--force': {'default': False, 'is_flag': True, 'help': help_msg.FORCE_CHECKOUT},
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION},
            '--version': {'default': -1, 'help': help_msg.ARTIFACT_VERSION},
            '--fail-limit': {'type': int, 'help': help_msg.FAIL_LIMIT},
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.STATUS_FULL_OPTION}
        },

        'arguments': {
            'ml-entity-tag': {},

        },

        'help': 'Checkout the ML_ENTITY_TAG|ML_ENTITY of a dataset into user workspace.'

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
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION},
            '--version': {'default': -1, 'help': help_msg.ARTIFACT_VERSION},
            '--fail-limit': {'type': int, 'help': help_msg.FAIL_LIMIT},
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.STATUS_FULL_OPTION}
        },

        'help': 'Checkout the ML_ENTITY_TAG|ML_ENTITY of a label set into user workspace.'

    },

    {
        'name': 'checkout',
        'callback': entity.checkout,
        'groups': [entity.models],
        'options': {
            ('--with-labels', '-l'): {'is_flag': True, 'default': False, 'help': help_msg.ASSOCIATED_WITH_LABELS},
            ('--with-dataset', '-d'): {'is_flag': True, 'default': False, 'help': help_msg.ASSOCIATED_WITH_DATASET},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},

            '--force': {'default': False, 'is_flag': True, 'help': help_msg.FORCE_CHECKOUT},
            '--bare': {'default': False, 'is_flag': True, 'help': help_msg.BARE_OPTION},
            '--version': {'default': -1, 'help': help_msg.ARTIFACT_VERSION},
            '--fail-limit': {'type': int, 'help': help_msg.FAIL_LIMIT},
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.STATUS_FULL_OPTION}
        },

        'arguments': {
            'ml-entity-tag': {},

        },

        'help': 'Checkout the ML_ENTITY_TAG|ML_ENTITY of a model set into user workspace.'

    },

    {
        'name': 'fetch',
        'callback': entity.fetch,
        'groups': [entity.datasets, entity.models, entity.labels],

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
        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {},
            'status_directory': {'required': False, 'default': ''}
        },

        'options': {
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.STATUS_FULL_OPTION},
        },

        'help': 'Print the files that are tracked or not and the ones that are in the index/staging area.'

    },

    {
        'name': 'diff',

        'callback': entity.diff,
        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {},
            'first_tag': {},
            'second_tag': {}
        },

        'options': {
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.STATUS_FULL_OPTION},
        },

        'help': 'Print the difference between two entity tag versions. The command will show added, updated and deleted files.'

    },

    {
        'name': 'show',

        'callback': entity.show,
        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'Print the specification file of the entity.'

    },

    {
        'name': 'add',
        'callback': entity.add,
        'groups': [entity.datasets, entity.labels],

        'arguments': {
            'ml-entity-name': {},
            'file-path': {'nargs': -1, 'required': False}
        },

        'options': {
            '--bumpversion': {'is_flag': True, 'default': False, 'help': help_msg.BUMP_VERSION},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION},
        },

        'help': 'Add %s change set ML_ENTITY_NAME to the local ml-git staging area.'

    },

    {
        'name': 'add',
        'callback': entity.add,
        'groups': [entity.models],

        'arguments': {
            'ml-entity-name': {},
            'file-path': {'nargs': -1, 'required': False}
        },

        'options': {
            '--bumpversion': {'is_flag': True, 'default': False, 'help': help_msg.BUMP_VERSION},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION},
            '--metric': {'required': False, 'multiple': True, 'type': (str, float), 'help': help_msg.METRIC_OPTION},
            '--metrics-file': {'type': NotEmptyString(), 'required': False, 'help': help_msg.METRICS_FILE_OPTION},
        },

        'help': 'Add %s change set ML_ENTITY_NAME to the local ml-git staging area.'

    },

    {
        'name': 'commit',
        'callback': entity.commit,
        'groups': [entity.datasets],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION},
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
            '--dataset': {'help': help_msg.LINK_DATASET_TO_LABEL, 'default': prompt_msg.EMPTY_FOR_NONE, 'prompt': prompt_msg.LINKED_DATASET_TO_LABEL_MESSAGE},
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION},
        },

        'help': 'Commit labels change set of ML_ENTITY_NAME locally to this ml-git repository.'

    },

    {
        'name': 'commit',
        'callback': entity.commit,
        'groups': [entity.models],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--dataset': {'help': help_msg.LINK_DATASET, 'default': prompt_msg.EMPTY_FOR_NONE, 'prompt': prompt_msg.LINKED_DATASET_TO_MODEL_MESSAGE},
            '--labels': {'help': help_msg.LINK_LABELS, 'default': prompt_msg.EMPTY_FOR_NONE, 'prompt': prompt_msg.LINKED_LABEL_TO_MODEL_MESSAGE},
            '--tag': {'help': help_msg.TAG_OPTION},
            '--version': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER},
            ('--message', '-m'): {'help': help_msg.COMMIT_MSG},
            '--fsck': {'is_flag': True, 'help': help_msg.FSCK_OPTION},
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

        'groups': [entity.datasets, entity.models, entity.labels],

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

        'groups': [entity.datasets, entity.models, entity.labels],

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
            '--storage-type': {
                'default': StorageType.S3.value, 'help': help_msg.STORAGE_TYPE_IMPORT_COMMAND,
                'type': click.Choice([StorageType.S3.value, StorageType.GDRIVE.value])
            },
            '--endpoint-url': {'default': '', 'help': help_msg.ENDPOINT_URL},
        },

        'help': 'This command allows you to download a file or directory from the S3 or Gdrive to ENTITY_DIR.'

    },

    {
        'name': 'export',

        'callback': entity.export_tag,

        'groups': [entity.datasets, entity.models, entity.labels],

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

        'help': 'This command allows you to export files from one storage (S3|MinIO) to another (S3|MinIO).'

    },

    {
        'name': 'update',

        'callback': entity.update,

        'groups': [entity.datasets, entity.models, entity.labels],

        'help': 'This command will update the metadata repository.'

    },

    {
        'name': 'branch',

        'callback': entity.branch,

        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'This command allows to check which tag is checked out in the ml-git workspace.'

    },

    {
        'name': 'remote-fsck',

        'callback': entity.remote_fsck,

        'groups': [entity.datasets, entity.models, entity.labels],

        'options': {
            '--thorough': {'is_flag': True, 'help': help_msg.THOROUGH_OPTION},
            '--paranoid': {'is_flag': True, 'help': help_msg.PARANOID_OPTION},
            '--retry': {'default': 2, 'help': help_msg.RETRY_OPTION},
            '--full': {'is_flag': True, 'default': False, 'help': help_msg.REMOTE_FSCK_FULL_OPTION},
        },

        'arguments': {
            'ml-entity-name': {}
        },

        'help': 'This command will check and repair the remote, by default it will only repair by uploading lacking chunks/blobs. '
                'Options bring more specialized repairs.'

    },

    {
        'name': 'create',

        'callback': entity.create,

        'groups': [entity.datasets, entity.models, entity.labels],

        'options': {
            '--categories': {'required': True, 'type': CategoriesType(), 'help': help_msg.CATEGORIES_OPTION, 'prompt': prompt_msg.CATEGORIES_MESSAGE},
            '--mutability': {'required': True, 'type': click.Choice(MutabilityType.to_list()),
                             'help': help_msg.MUTABILITY, 'prompt': prompt_msg.MUTABILITY_MESSAGE},
            '--storage-type': {
                'type': click.Choice(MultihashStorageType.to_list(),
                                     case_sensitive=True),
                'help': help_msg.STORAGE_TYPE_MULTIHASH, 'default': StorageType.S3H.value
            },
            '--version': {'type': click.IntRange(0, int(8 * '9')), 'help': help_msg.SET_VERSION_NUMBER, 'default': 1},
            '--import': {'help': help_msg.IMPORT_OPTION, 'type': NotEmptyString(),
                         'cls': MutuallyExclusiveOption, 'mutually_exclusive': ['import_url', 'credentials_path']},
            '--wizard-config': {'is_flag': True, 'help': help_msg.WIZARD_CONFIG},
            '--bucket-name': {'type': NotEmptyString(), 'help': help_msg.BUCKET_NAME},
            '--import-url': {'help': help_msg.IMPORT_URL,
                             'type': NotEmptyString(),
                             'cls': MutuallyExclusiveOption, 'mutually_exclusive': ['import']},
            '--credentials-path': {'default': None, 'type': NotEmptyString(), 'help': help_msg.CREDENTIALS_PATH,
                                   'cls': OptionRequiredIf, 'required_option': ['import-url']},
            '--unzip': {'help': help_msg.UNZIP_OPTION, 'is_flag': True},
            '--entity-dir': {'type': NotEmptyString(), 'help': help_msg.ENTITY_DIR}
        },

        'arguments': {
            'artifact-name': {},
        },

        'help': help_msg.CREATE_COMMAND

    },

    {
        'name': 'unlock',

        'callback': entity.unlock,

        'groups': [entity.datasets, entity.models, entity.labels],

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

        'groups': [entity.datasets, entity.models, entity.labels],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--stat': {'is_flag': True, 'help': help_msg.STAT_OPTION, 'default': False},
            '--fullstat': {'is_flag': True, 'help': help_msg.FULL_STAT_OPTION, 'default': False},
        },

        'help': 'This command shows ml-entity-name\'s commit information like author, date, commit message.'

    },

    {
        'name': 'add',

        'callback': storage.storage_add,

        'groups': [storage.storage],

        'arguments': {
            'bucket-name': {},
        },

        'options': {
            '--credentials': {'help': help_msg.STORAGE_CREDENTIALS},
            '--type': {'default': StorageType.S3H.value,
                       'type': click.Choice(MultihashStorageType.to_list(), case_sensitive=True),
                       'help': help_msg.STORAGE_TYPE_MULTIHASH,
                       'prompt': prompt_msg.STORAGE_TYPE_MESSAGE},
            '--region': {'help': help_msg.STORAGE_REGION},
            '--endpoint-url': {'help': help_msg.ENDPOINT_URL},
            '--username': {'help': help_msg.USERNAME},
            '--private-key': {'help': help_msg.PRIVATE_KEY},
            '--port': {'help': help_msg.PORT, 'default': 22},
            ('--global', '-g'): {'is_flag': True, 'default': False, 'help': help_msg.GLOBAL_OPTION},
        },

        'help': help_msg.STORAGE_ADD_COMMAND

    },

    {
        'name': 'del',

        'callback': storage.storage_del,

        'groups': [storage.storage],

        'arguments': {
            'bucket-name': {},
        },

        'options': {
            '--type': {'default': StorageType.S3H.value,
                       'type': click.Choice(MultihashStorageType.to_list(),
                                            case_sensitive=True),
                       'help': help_msg.STORAGE_TYPE_MULTIHASH},
            ('--global', '-g'): {'is_flag': True, 'default': False, 'help': help_msg.GLOBAL_OPTION},
        },

        'help': 'Delete a storage BUCKET_NAME from ml-git.'

    },

    {
        'name': 'metrics',

        'callback': entity.metrics,

        'groups': [entity.models],

        'arguments': {
            'ml-entity-name': {},
        },

        'options': {
            '--export-type': {'required': False, 'help': help_msg.EXPORT_METRICS_TYPE,
                              'type': click.Choice(FileType.to_list(), case_sensitive=False)},
            '--export-path': {'help': help_msg.EXPORT_METRICS_PATH,
                              'cls': OptionRequiredIf, 'required_option': ['export-type']},
        },

        'help': help_msg.METRICS_COMMAND

    }

]


def define_command(descriptor):
    callback = descriptor['callback']

    command = click.command(name=descriptor['name'], short_help=descriptor['help'], cls=DeprecatedOptionsCommand)(click.pass_context(callback))

    if 'arguments' in descriptor:
        for key, value in descriptor['arguments'].items():
            command = click.argument(key, **value)(command)

    config_file = merged_config_load()
    if 'options' in descriptor:
        for key, value in descriptor['options'].items():
            if WIZARD_ENABLE_KEY in config_file and not config_file[WIZARD_ENABLE_KEY]:
                value.pop('prompt', None)
            if type(key) == tuple:
                click_option = click.option(*key, **value)
            else:
                click_option = click.option(key, **value)
            command = click_option(command)

    command = click.help_option(hidden=True)(command)
    verbose_option = click.option('--verbose', is_flag=True, expose_value=False, callback=set_verbose_mode,
                                  help=help_msg.VERBOSE_OPTION)
    command = verbose_option(command)

    for group in descriptor['groups']:
        command_copy = copy.deepcopy(command)
        if '%s' in descriptor['help']:
            command_copy.short_help = descriptor['help'] % group.name
        group.add_command(command_copy)


for description in commands:
    define_command(description)
