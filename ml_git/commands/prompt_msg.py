"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

CATEGORIES_MESSAGE = 'At least one category must be defined. The categories\' names must be comma-separated. ' \
                     'Please inform the value for the categories option'
WANT_LINK_TO_MODEL_ENTITY = 'Do you want to link a {} entity to this version of the model'
WANT_LINK_TO_LABEL_ENTITY = 'Do you want to link a {} entity to this version of the labels set'
DEFINE_LINKED_DATASET = '\tDefine the dataset name to be linked'
DEFINE_LINKED_LABELS = '\tDefine the labels name to be linked'
MUTABILITY_MESSAGE = 'An entity must have a defined mutability. Please inform the value for the mutability option'
EMPTY_FOR_NONE = 'empty for none'
STORAGE_TYPE_MESSAGE = 'Define the storage type'
INVALID_STORAGE_TYPE_MESSAGE = "Invalid choice: {}. Choose a valid option"
CREDENTIALS_PROFILE_MESSAGE = 'Define the profile to be used to connect to S3 [default]'
CREDENTIALS_PATH_MESSAGE = 'Define the path to the credentials that will be used to connect to GDrive [\'.\']'
REGION_MESSAGE = 'Define the AWS region name for the storage [us-east-1]'
ENDPOINT_MESSAGE = 'If you are using MinIO define the endpoint URL [None]'
SFTPH_ENDPOINT_MESSAGE = 'Define the endpoint URL [None]'
THOROUGH_MESSAGE = 'Do you want to download the IPLD if it is not present in the local repository?'
USERNAME_SFTPH = 'Define the username for the SFTP login [None]'
PRIVATE_KEY_SFTPH = 'Define the full path for the private key file [None]'
PORT_SFTPH = 'Define the SFTP port that will be used [22]'
METRIC_FILE = 'If you have a file with the metrics of this model you can associate it with this version of the entity,' \
              ' define the path to the file [None]'
COMMIT_VERSION = 'Define the {} version to be commited [{}]'
COMMIT_MESSAGE = 'Define the commit message'
