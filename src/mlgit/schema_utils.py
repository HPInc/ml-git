"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from schema import Schema, And, Use, SchemaError, Or


def main_validate(arguments):
    schema = Schema({
        '--retry': Or(None, And(Use(int), lambda n: 0 < n), error='--retry=<retries> should be integer (0 < retries)')},
        ignore_extra_keys=True)
    try:
        schema.validate(arguments)
    except SchemaError as e:
        exit(e)