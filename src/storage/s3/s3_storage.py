"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from repository import ml_git_environment
from storage.s3.S3Credentials import S3Credentials
from utils import json_utils


def _load_credentials_from_json():
    try:
        default_path = Path.home().joinpath('.ml-git', 'credentials.json')
        custom_path = ml_git_environment.REPOSITORY_CONFIG_PROFILE.s3_credentials_path
        json_path = custom_path if os.path.isfile(custom_path) else default_path
        json = json_utils.read_json(json_path)
        return S3Credentials(json['aws_bucket_name'], json['aws_default_region'], json['aws_access_key_id'],
                             json['aws_secret_access_key'])
    except FileNotFoundError:
        return S3Credentials()


def _load_credentials_from_config():
    config_profile = ml_git_environment.REPOSITORY_CONFIG_PROFILE
    return S3Credentials(config_profile.s3_bucket, config_profile.s3_region, config_profile.s3_access_key,
                         config_profile.s3_secret_key)


def assert_and_get_s3_setup():
    cred_json = _load_credentials_from_json()
    cred_config = _load_credentials_from_config()

    if not cred_json.is_valid() and not cred_config.is_valid():
        raise Exception(
            f'AWS S3 setup is not finished. Run \'ml-git config\' to setup your AWS S3 credentials.')
    return cred_json if cred_json.is_valid() else cred_config


def put_object(src_data):
    credentials = assert_and_get_s3_setup()

    file_name = Path(src_data).name
    if isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception:
            raise Exception('upload error')
    else:
        raise Exception('upload error')

    # Put the object
    s3 = boto3.client(
        "s3",
        region_name=credentials.region,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key
    )

    try:
        resp = s3.put_object(Bucket=credentials.bucket, Key=file_name, Body=object_data)
    except ClientError:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        raise Exception('upload error')
    return concat_s3_url(resp, credentials.bucket, file_name)


def concat_s3_url(response, bucket_name, file_name):
    return f'https://s3.amazonaws.com/{bucket_name}/{file_name}?versionId{response["VersionId"]}'
