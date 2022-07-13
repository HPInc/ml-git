"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
from click.testing import CliRunner

from ml_git.commands import entity, prompt_msg
from ml_git.commands.utils import MAX_INT_VALUE
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_REMOTE_FSCK, MLGIT_PUSH, MLGIT_COMMIT
from tests.integration.helper import ML_GIT_DIR, ERROR_MESSAGE, MLGIT_ADD, DATASETS, DATASET_NAME
from tests.integration.helper import check_output, init_repository, MINIO_BUCKET_PATH


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class RemoteFsckAcceptanceTests(unittest.TestCase):
    file = 'zdj7WWzF6t7MVbteB97N39oFQjP9TTYdHKgS2wetdFWuj1ZP1'

    def setup_remote_fsck(self, entity=DATASETS):
        init_repository(entity, self)

        with open(os.path.join(entity, entity+'-ex', 'remote'), 'wt') as z:
            z.write(str('0' * 10011))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity+'-ex', '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata'), entity+'-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity+'-ex', '')))

        HEAD = os.path.join(ML_GIT_DIR, entity, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity+'-ex')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_remote_fsck(self):
        self.setup_remote_fsck()
        os.unlink(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj'))
        output = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME))
        self.assertIn(output_messages['INFO_STARTING_IPLDS_CHECK'], output)
        self.assertIn(output_messages['INFO_STARTING_BLOBS_CHECK'], output)
        self.assertIn(output_messages['INFO_FSCK_COMPLETE'], output)
        self.assertIn(output_messages['INFO_REMOTE_FSCK_FIXED'] % (0, 1), output)
        self.assertIn(output_messages['INFO_REMOTE_FSCK_TOTAL'] % (1, 1), output)
        self.assertTrue(os.path.exists(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj')))

    def _get_file_path(self):
        hash_path = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects', 'hashfs')
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

        self.assertIn(output_messages['INFO_MISSING_DESCRIPTOR_FILES'] % 1, check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME)))

        self.assertFalse(os.path.exists(file_path))

        self.assertIn(output_messages['INFO_MISSING_DESCRIPTOR_FILES_DOWNLOAD'] % 1, check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME) + ' --thorough'))

        self.assertTrue(os.path.exists(file_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_remote_fsck_paranoid(self):
        self.setup_remote_fsck()
        self._get_file_path()

        os.unlink(os.path.join(MINIO_BUCKET_PATH, self.file))

        with open(os.path.join(MINIO_BUCKET_PATH, self.file), 'wt') as z:
            z.write(str('1' * 10011))

        output = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME) + ' --paranoid')

        self.assertNotIn(output_messages['DEBUG_CORRUPTION_DETECTED_FOR'] % self.file, output)  # msg is debug-only
        self.assertIn(output_messages['INFO_REMOTE_FSCK_FIXED'] % (1, 0), output)

        self.assertNotIn(output_messages['DEBUG_CORRUPTION_DETECTED_FOR'], check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME) + ' --paranoid'))
        self.assertTrue(os.path.exists(os.path.join(MINIO_BUCKET_PATH, self.file)))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_04_remote_fsck_with_full_option(self):
        self.setup_remote_fsck()
        os.unlink(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj'))
        output = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME + ' --full'))
        self.assertIn(output_messages['INFO_REMOTE_FSCK_FIXED'] % (0, 1), output)
        self.assertTrue(os.path.exists(os.path.join(MINIO_BUCKET_PATH, 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj')))
        self.assertIn(output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('Blobs', ['zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj']), output)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_05_remote_fsck_empty_entity(self):
        init_repository(DATASETS, self)
        output = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME))
        self.assertIn(output_messages['WARN_EMPTY_ENTITY'] % DATASET_NAME, output)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_06_remote_fsck_missing_descriptor_files(self):
        self.setup_remote_fsck()
        file_path = self._get_file_path()
        os.remove(file_path)

        message = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME))
        self.assertIn(output_messages['INFO_MISSING_DESCRIPTOR_FILES'] % 1, message)
        self.assertIn(output_messages['INFO_SEE_COMPLETE_LIST_OF_MISSING_FILES'], message)

        message = check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME + ' --full'))
        self.assertIn(output_messages['INFO_MISSING_DESCRIPTOR_FILES'] % 1, message)
        self.assertIn(output_messages['INFO_LIST_OF_MISSING_FILES'] % '[', message)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_07_remote_fsck_with_wizard_enabled(self):
        self.setup_remote_fsck()
        file_path = self._get_file_path()
        os.remove(file_path)
        self.assertIn(output_messages['INFO_MISSING_DESCRIPTOR_FILES'] % 1, check_output(MLGIT_REMOTE_FSCK % (DATASETS, DATASET_NAME)))
        self.assertFalse(os.path.exists(file_path))
        runner = CliRunner()
        result = runner.invoke(entity.datasets, ['remote-fsck', DATASET_NAME, '--wizard'], input='y\n')
        self.assertIn(prompt_msg.THOROUGH_MESSAGE, result.output)
        self.assertTrue(os.path.exists(file_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_08_remote_fsck_with_wizard_enabled_to_retry(self):
        not_a_number = 'aaaaaa'
        out_range = int(10 * '9')
        valid_number = 55
        runner = CliRunner()
        result = runner.invoke(entity.datasets,
                               ['remote-fsck', DATASET_NAME, '--wizard', '--retry='],
                               input='{}\n{}\n{}'.format(not_a_number, out_range, valid_number))
        self.assertIn(output_messages['ERROR_EMPTY_VALUE'], result.output)
        self.assertIn(output_messages['ERROR_NOT_INTEGER_VALUE'].format(not_a_number), result.output)
        self.assertIn(output_messages['ERROR_VALUE_NOT_IN_RANGE'].format(out_range, 0, MAX_INT_VALUE), result.output)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_09_remote_fsck_with_retry_out_range(self):
        out_range = int(10 * '9')
        runner = CliRunner()
        result = runner.invoke(entity.datasets, ['remote-fsck', DATASET_NAME, '--retry={}'.format(out_range)])
        self.assertIn(output_messages['ERROR_VALUE_NOT_IN_RANGE'].format(out_range, 0, MAX_INT_VALUE), result.output)
