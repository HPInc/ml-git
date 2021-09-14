"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import pathlib
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT, MLGIT_CREATE, MLGIT_ADD
from tests.integration.helper import ERROR_MESSAGE, create_spec, add_file, ML_GIT_DIR, clear, SFTP_BUCKET_PATH, \
    FAKE_SSH_KEY_PATH, DATASETS, DATASET_NAME, SFTPH, STRICT
from tests.integration.helper import check_output, GIT_PATH


@pytest.mark.usefixtures('tmp_dir', 'start_local_git_server', 'switch_to_tmp_dir')
class SFTPAcceptanceTests(unittest.TestCase):
    repo_type = DATASETS
    storage_type = SFTPH
    bucket = 'mlgit'
    workspace = os.path.join(DATASETS, DATASET_NAME)

    def set_up_push(self, create_know_file=False):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, self.tmp_dir, version=1, mutability=STRICT, storage_type=self.storage_type)

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, self.bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   ('mlgit --username=mlgit_user '
                                    '--endpoint-url=127.0.0.1 --port=9922 --private-key=' + FAKE_SSH_KEY_PATH, self.storage_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % DATASETS))

        if create_know_file:
            with open(os.path.join(self.repo_type, DATASET_NAME, 'file'), 'wt') as z:
                z.write(str('0' * 10011))
        add_file(self, self.repo_type, '', 'new')

        metadata_path = os.path.join(ML_GIT_DIR, self.repo_type, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, metadata_path), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (self.repo_type, DATASET_NAME, '')))
        HEAD = os.path.join(ML_GIT_DIR, self.repo_type, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

    def check_amount_of_files(self, expected_files):
        file_count = 0
        for path in pathlib.Path(SFTP_BUCKET_PATH).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_create_sftp_storage(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type), check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, self.bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   ('mlgit --username=mlgit_user '
                                    '--endpoint-url=127.0.0.1 --port=9922 --private-key=' + FAKE_SSH_KEY_PATH, self.storage_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_push_file(self):
        self.set_up_push()
        number_of_files_in_bucket = 0
        self.check_amount_of_files(number_of_files_in_bucket)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))
        number_of_files_in_bucket = 10
        self.check_amount_of_files(number_of_files_in_bucket)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_checkout(self):
        self.set_up_push()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))
        clear(self.workspace)
        clear(os.path.join(ML_GIT_DIR, self.repo_type))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (self.repo_type, DATASET_NAME)))
        ws_path = os.path.join(self.tmp_dir, self.repo_type, DATASET_NAME)
        self.assertTrue(os.path.exists(ws_path))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile0')))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile1')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_push_with_wrong_bucket(self):
        clear(SFTP_BUCKET_PATH)
        os.mkdir(SFTP_BUCKET_PATH)
        wrong_bucket = 'wrong_bucket'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, wrong_bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   (wrong_bucket, self.storage_type + ' --username=mlgit_user '
                                                                      '--port=9922 --endpoint-url=127.0.0.1 --private-key=' + FAKE_SSH_KEY_PATH)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))

        self.assertNotIn(ERROR_MESSAGE, check_output(
            MLGIT_CREATE % (DATASETS, DATASET_NAME + ' --storage-type=sftph --mutability=strict --categories=test '
                                                     '--bucket-name=wrong_bucket')))
        add_file(self, self.repo_type, '', 'new')

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (self.repo_type, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (self.repo_type, DATASET_NAME, '')))
        number_of_files_in_bucket = 0
        self.check_amount_of_files(number_of_files_in_bucket)
        self.assertIn(output_messages['ERROR_BUCKET_DOES_NOT_EXIST'] % wrong_bucket, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))
        self.check_amount_of_files(number_of_files_in_bucket)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_push_with_fail(self):
        clear(SFTP_BUCKET_PATH)
        os.mkdir(SFTP_BUCKET_PATH)
        self.set_up_push(create_know_file=True)

        object_path = os.path.join(self.tmp_dir, '.ml-git', self.repo_type, 'objects',
                                   'hashfs', 'i9', '96', 'zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj')
        clear(object_path)
        number_of_files_in_bucket = 0
        self.check_amount_of_files(number_of_files_in_bucket)
        self.assertIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME + ' --clearonfail')))
