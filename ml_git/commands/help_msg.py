"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

RETRY_OPTION = 'Number of retries to download the files from the storage [default: 2].'
FORCE_CHECKOUT = 'Force checkout command to delete untracked/uncommitted files from local repository.'
BARE_OPTION = 'Ability to add/commit/push without having the ml-entity checked out.'
FSCK_OPTION = 'Run fsck after command execution.'
TAG_OPTION = 'Ml-git tag to identify a specific version of a ML entity.'
COMMIT_MSG = 'Use the provided <msg> as the commit message.'
NOT_IMPLEMENTED = 'Not implemented yet'
CLEAR_ON_FAIL = 'Remove the files from the storage in case of failure during the push operation.'
SAMPLING_OPTION = 'group: <amount>:<group> The group sample option consists of '\
                  'amount and group used to download a sample.\n'\
                  'range: <start:stop:step> The range sample option consists of '\
                  'start, stop and step used to download a sample. The start '\
                  'parameter can be equal or greater than zero.'\
                  'The stop parameter can be \'all\', -1 or'\
                  ' any integer above zero.\nrandom: <amount:frequency> '\
                  'The random sample option consists of '\
                  'amount and frequency used to download a sample.'
SEED_OPTION = 'Seed to be used in random-based samplers.'
ASSOCIATED_WITH_DATASET = 'The checkout associated dataset in user workspace as well.'
ASSOCIATED_WITH_LABELS = 'The checkout associated labels  in user workspace as well.'
BUMP_VERSION = 'Increment the version number when adding more files.'
LINK_DATASET = 'Link dataset entity name to this model set version.'
LINK_LABELS = 'Link labels entity name to this model set version.'
RESET_HARD = 'Remove untracked files from workspace, files to be committed from staging area as well '\
             'as committed files upto <reference>.'
RESET_MIXED = 'Revert the committed files and the staged files to \'Untracked Files\'. This is the default action.'
RESET_SOFT = 'Revert the committed files to \'Changes to be committed\'.'
RESET_REFENCE = 'head:Will keep the metadata in the current commit.' \
                       '\nhead~1:Will move the metadata to the last commit.'
CREDENTIALS_OPTION = 'Input your profile to an s3 storage or your credentials' \
                     ' path to a gdrive storage.(eg, --credentials=path/to/.credentials'
REGION_OPTION = 'AWS region name [default: us-east-1].'
PATH_OPTION = 'Storage folder path.'
OBJECT_OPTION = 'Filename in storage.'
ENDPOINT_URL = 'Storage endpoint url.'
USERNAME = 'The username for the sftp login.'
PRIVATE_KEY = 'Full path for the private key file.'
PORT = 'SFTP port [default: 22].'
AWS_CREDENTIALS = 'Profile of AWS credentials [default: default].'
THOROUGH_OPTION = 'Try to download the IPLD if it is not present in the local repository to verify' \
                  ' the existence of all contained IPLD links associated.'
PARANOID_OPTION = 'Adds an additional step that will download all ' \
                  'IPLD and its associated IPLD links to verify the content by ' \
                  'computing the multihash of all these.'
CATEGORIES_OPTION = 'Artifact\'s categories name. The categories name must be separated by comma. E.g: "category1,category2,category3"'
STORAGE_TYPE = 'Data storage type [default: s3h].'
VERSION_NUMBER = 'Number of artifact version.'
IMPORT_OPTION = 'Path to be imported to the project.'
WIZARD_CONFIG = 'If specified, ask interactive questions at console for git & storage configurations.'
BUCKET_NAME = 'Bucket name'
IMPORT_URL = 'Import data from a google drive url.'
CREDENTIALS_PATH = 'Directory of credentials.json.'
UNZIP_OPTION = 'Unzip imported zipped files. Only available if --import-url is used.'
STAT_OPTION = 'Show amount of files and size of an ml-entity.'
FULL_STAT_OPTION = 'Show added and deleted files.'
SET_VERSION_NUMBER = 'Set the version number of the artifact. This number must be in the range 0 to 999999999.'
ARTIFACT_VERSION = 'Number of artifact version to be downloaded [default: latest].'
MUTABILITY = 'Mutability type.'
STATUS_FULL_OPTION = 'Show all contents for each directory.'
STORAGE_CREDENTIALS = 'Profile name for storage credentials'
STORAGE_REGION = 'AWS region name for S3 bucket'
STORAGE_TYPE = 'Storage type (s3h, s3, azureblobh, gdriveh ...) [default: s3h]'
GLOBAL_OPTION = 'Use this option to set configuration at global level'
ENTITY_DIR = 'The relative path where the entity will be created inside the ml entity directory.'
METRICS_FILE_OPTION = 'Metrics file path.'
METRIC_OPTION = 'Metric key and value.'
METRICS_COMMAND = 'Shows metrics information for each tag of the entity.'
EXPORT_METRICS_PATH = 'Set the path to export metrics to a file.'
EXPORT_METRICS_TYPE = 'Choose the format of the file that will be generated with the metrics [default: json].'
FAIL_LIMIT = 'Number of failures before aborting the command [default: no limit].'
LOCAL_CONFIGURATIONS = 'Local configurations.'
GLOBAL_CONFIGURATIONS = 'Global configurations.'
VERBOSE_OPTION = 'Debug mode'
