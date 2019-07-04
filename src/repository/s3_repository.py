"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import utils.json_utils as j_util


credentials = j_util.read_json(Path.home().joinpath('.ml-git', 'credentials.json'))


def put_object(src_data):

    file_name = Path(src_data).name
    if isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            raise Exception('upload error')
    else:
        raise Exception('upload error')

    # Put the object
    s3 = boto3.client(
            "s3",
            region_name=credentials['aws_default_region'],
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key']
            )

    try:
        resp = s3.put_object(Bucket=credentials['aws_bucket_name'], Key=file_name, Body=object_data)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        raise Exception('upload error')
    return concat_s3_url(resp, credentials['aws_bucket_name'], file_name)


def concat_s3_url(response, bucket_name, file_name):
    url = f'https://s3.amazonaws.com/{bucket_name}/{file_name}?versionId{response["VersionId"]}'
    return url




