"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_REMOTE_FSCK, MLGIT_PUSH, MLGIT_COMMIT
from tests.integration.helper import ML_GIT_DIR, ERROR_MESSAGE, MLGIT_ADD
from tests.integration.helper import check_output, init_repository, MINIO_BUCKET_PATH
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class RemoteFsckAcceptanceTests(unittest.TestCase):
    file = 'zdj7WWzF6t7MVbteB97N39oFQjP9TTYdHKgS2wetdFWuj1ZP1'

    def setup_remote_fsck(self, entity='dataset'):
        init_repository(entity, self)

        with open(os.path.join(entity, entity+'-ex', 'remote'), 'wt') as z:
            z.write(str('0' * 10011))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity+'-ex', '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata'),
                                      os.path.join('computer-vision', 'images', entity+'-ex')),
                      check_output(MLGIT_COMMIT % (entity, entity+'-ex', '')))

        HEAD = os.path.join(ML_GIT_DIR, entity, 'refs', 'dataset-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity+'-ex')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_remote_fsck(self):
        self.setup_remote_fsck()
        os.unlink(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj'))
        self.assertIn(messages[35] % (0, 1), check_output(MLGIT_REMOTE_FSCK % ('dataset', 'dataset-ex')))
        self.assertTrue(os.path.exists(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj')))

    def _get_file_path(self):
        hash_path = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'objects', 'hashfs')
        file_path = ''

        for root, _, files in os.walk(hash_path):
            for f in files:
                if f == self.file:
                    file_path = os.path.join(root, f)

        self.assertTrue(os.path.exists(file_path))
        return file_path

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_remote_fsck_thorough(self):
        self.setup_remote_fsck()
        file_path = self._get_file_path()

        os.remove(file_path)

        self.assertIn(messages[58] % 1, check_output(MLGIT_REMOTE_FSCK % ('dataset', 'dataset-ex')))

        self.assertFalse(os.path.exists(file_path))

        self.assertIn(messages[59] % 1, check_output(MLGIT_REMOTE_FSCK % ('dataset', 'dataset-ex') + ' --thorough'))

        self.assertTrue(os.path.exists(file_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_remote_fsck_paranoid(self):
        self.setup_remote_fsck()
        self._get_file_path()

        os.unlink(os.path.join(MINIO_BUCKET_PATH, self.file))

        with open(os.path.join(MINIO_BUCKET_PATH, self.file), 'wt') as z:
            z.write(str('1' * 10011))

        output = check_output(MLGIT_REMOTE_FSCK % ('dataset', 'dataset-ex') + ' --paranoid')

        self.assertIn(messages[60] % self.file, output)
        self.assertIn(messages[35] % (1, 0), output)

        self.assertNotIn(messages[60], check_output(MLGIT_REMOTE_FSCK % ('dataset', 'dataset-ex') + ' --paranoid'))
        self.assertTrue(os.path.exists(os.path.join(MINIO_BUCKET_PATH, self.file)))
