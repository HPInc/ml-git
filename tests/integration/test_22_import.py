"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import unittest

import pytest

from tests.integration.commands import MLGIT_IMPORT
from tests.integration.helper import check_output, init_repository, PROFILE
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class ImportAcceptanceTests(unittest.TestCase):

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(entity_type, entity_type+'-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_import_with_wrong_credentials(self):
        init_repository('dataset', self)

        self.assertIn(messages[54], check_output(MLGIT_IMPORT % ('dataset', 'bucket', 'dataset-ex')
                                                 + ' --credentials=personal2'))
        self.check_amount_of_files('dataset', 1)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_import_with_wrong_bucket(self):
        init_repository('dataset', self)

        self.assertIn(messages[51], check_output(MLGIT_IMPORT % ('dataset', 'wrong-bucket', 'dataset-ex')
                                                 + ' --object=test  --credentials='+PROFILE))
        self.check_amount_of_files('dataset', 1)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_import_when_credentials_does_not_exist(self):
        init_repository('dataset', self)

        self.assertIn(messages[52] % 'anyone', check_output(MLGIT_IMPORT % ('dataset', 'bucket', 'dataset-ex')
                                                            + ' --credentials=anyone'))
        self.check_amount_of_files('dataset', 1)
