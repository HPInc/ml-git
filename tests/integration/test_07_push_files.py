"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH
from tests.integration.helper import ML_GIT_DIR, MINIO_BUCKET_PATH, GIT_PATH
from tests.integration.helper import check_output, clear, init_repository, add_file, ERROR_MESSAGE


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class PushFilesAcceptanceTests(unittest.TestCase):

    def _push_entity(self, entity_type):
        clear(os.path.join(MINIO_BUCKET_PATH, 'zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12'))
        init_repository(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new', file_content='0')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, os.path.join('computer-vision', 'images', entity_type + '-ex')),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type+'-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))
        os.chdir(metadata_path)
        self.assertTrue(os.path.exists(
            os.path.join(MINIO_BUCKET_PATH, 'zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12')))
        self.assertIn('computer-vision__images__' + entity_type + '-ex__2', check_output('git describe --tags'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_push_files_to_dataset(self):
        self._push_entity('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_push_files_to_labels(self):
        self._push_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_push_files_to_model(self):
        self._push_entity('model')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_push_with_wrong_repository(self):
        init_repository('dataset', self)
        add_file(self, 'dataset', '--bumpversion', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ('dataset',  'dataset-ex', '')))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs', 'dataset-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        git_path = os.path.join(self.tmp_dir, GIT_PATH)

        clear(git_path)

        output = check_output(MLGIT_PUSH % ('dataset', 'dataset-ex'))

        self.assertIn(ERROR_MESSAGE, output)
        self.assertIn(git_path, output)
