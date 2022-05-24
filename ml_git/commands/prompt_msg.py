"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

CATEGORIES_MESSAGE = 'At least one category must be defined. The categories\' names must be comma-separated. ' \
                     'Please inform the value for the categories option'
LINKED_DATASET_TO_MODEL_MESSAGE = 'Link a dataset entity name to this model set version'
LINKED_LABEL_TO_MODEL_MESSAGE = 'Link a labels entity name to this model set version'
LINKED_DATASET_TO_LABEL_MESSAGE = 'Link a dataset entity name to this label set version'
MUTABILITY_MESSAGE = 'An entity must have a defined mutability. Please inform the value for the mutability option'
EMPTY_FOR_NONE = 'empty for none'
STORAGE_TYPE_MESSAGE = 'Define the storage type'
CREDENTIALS_PROFILE_MESSAGE = 'Define the profile to be used to connect to S3 [default]'
CREDENTIALS_PATH_MESSAGE = 'Define the path to the credentials that will be used to connect to GDrive [\'.\']'
REGION_MESSAGE = 'Define the AWS region name for the storage [us-east-1]'
ENDPOINT_MESSAGE = 'If you are using MinIO define the endpoint URL [None]'
USERNAME_SFTPH = 'Define the username for the SFTP login [None]'
PRIVATE_KEY_SFTPH = 'Define the full path for the private key file [\'.\']'
PORT_SFTPH = 'Define the SFTP port that will be used [22]'
METRIC_FILE = 'If you have a file with the metrics of this model you can associate it with this version of the entity,' \
              ' define the path to the file [None]'
BUMP_VERSION = 'Do tou want to increment the version number when adding more files.'
