"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import logging
import boto3
from botocore.exceptions import ClientError
import utils.json_utils as j_util


credentials = j_util.read_json('../utils/credentials.json')


def put_object(dest_bucket_name, dest_object_name, src_data):

    if isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            logging.error(e)
            return False
    else:
        logging.error('Type of ' + str(type(src_data)) +
                      ' for the argument \'src_data\' is not supported.')
        return False

    # Put the object
    s3 = boto3.client(
            "s3",
            region_name=credentials['aws_default_region'],
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key']
            )

    try:
        resp = s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        logging.error(e)
        return False
    logging.info("uploaded file")
    return concat_s3_url(resp, dest_bucket_name, dest_object_name)


def concat_s3_url(response, bucket_name, file_name):
    url = f'https://s3.amazonaws.com/{bucket_name}/{file_name}?versionId{response["VersionId"]}'
    return url
