"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest

import pytest

from tests.integration.commands import MLGIT_INIT, MLGIT_CONFIG
from tests.integration.helper import check_output
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class ConfigAcceptanceTests(unittest.TestCase):
    expected_result = "config:\n{'batch_size': 20,\n 'cache_path': '',\n 'dataset': {'git': ''}," \
                      "\n 'index_path': '',\n 'labels': {'git': ''},\n 'metadata_path': '',\n 'mlgit_conf': 'config.yaml'," \
                      "\n 'mlgit_path': '.ml-git',\n 'model': {'git': ''},\n 'object_path': '',\n 'push_threads_count': 30,\n 'refs_path': ''," \
                      "\n 'store': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'}," \
                      "\n                                     'region': 'us-east-1'}}},\n 'verbose': 'info'}"

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_config_command(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(self.expected_result, check_output(MLGIT_CONFIG))
