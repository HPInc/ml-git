"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_LOG
from tests.integration.helper import ML_GIT_DIR, add_file, create_spec, delete_file, ERROR_MESSAGE
from tests.integration.helper import check_output, init_repository
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class LogTests(unittest.TestCase):
    COMMIT_MESSAGE = 'test_message'
    TAG = 'computer-vision__images__dataset-ex__1'

    def setUp_test(self):
        init_repository('dataset', self)
        create_spec(self, 'dataset', self.tmp_dir)
        self.assertIn(messages[13] % 'dataset', check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '-m ' + self.COMMIT_MESSAGE)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_log(self):
        self.setUp_test()
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', ''))
        self.assertIn(messages[77] % self.TAG, output)
        self.assertIn(messages[78] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[79] % 0, output)
        self.assertNotIn(messages[80] % 0, output)
        self.assertNotIn(messages[81], output)
        self.assertNotIn(messages[82], output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_log_with_stat(self):
        self.setUp_test()
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--stat'))
        self.assertIn(messages[79] % 0, output)
        self.assertIn(messages[80] % 0, output)
        self.assertNotIn(messages[81] % 0, output)
        self.assertNotIn(messages[82] % 0, output)
        self.assertNotIn(messages[83] % 0, output)
        self.assertNotIn(messages[84] % 0, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_log_with_fullstat(self):
        self.setUp_test()
        add_file(self, 'dataset', '--bumpversion')
        check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', ''))
        amount_files = 5
        workspace_size = 14

        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--fullstat'))

        files = ['newfile4', 'file2', 'file0', 'file3']

        for file in files:
            self.assertIn(file, output)

        self.assertIn(messages[84] % amount_files, output)
        self.assertIn(messages[83] % workspace_size, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_log_with_fullstat_files_added_and_deleted(self):
        self.setUp_test()
        add_file(self, 'dataset', '--bumpversion')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        added = 4
        deleted = 1
        workspace_path = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex')
        files = ['file2', 'newfile4']
        delete_file(workspace_path, files)
        add_file(self, 'dataset', '--bumpversion', 'img')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--fullstat'))
        self.assertIn(messages[81] % added, output)
        self.assertIn(messages[82] % deleted, output)
