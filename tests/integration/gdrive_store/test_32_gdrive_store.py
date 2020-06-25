"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_IMPORT
from tests.integration.helper import ML_GIT_DIR, CREDENTIALS_PATH
from tests.integration.helper import check_output, clear, init_repository, add_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class GdrivePushFilesAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_01_push_and_checkout(self):
        cpath = 'credentials-json'
        init_repository('dataset', self, store_type='gdriveh', profile=cpath)
        add_file(self, 'dataset', '--bumpversion', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata')
        self.assertIn(messages[17] % (metadata_path, os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output('ml-git dataset commit dataset-ex'))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs', 'dataset-ex', 'HEAD')

        self.assertTrue(os.path.exists(HEAD))
        check_output('ml-git dataset push dataset-ex')
        os.chdir(metadata_path)

        tag = 'computer-vision__images__dataset-ex__2'
        self.assertIn(tag, check_output('git describe --tags'))

        os.chdir(self.tmp_dir)

        workspace = os.path.join(self.tmp_dir, 'dataset')
        clear(workspace)
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        init_repository('dataset', self, store_type='gdriveh', profile=cpath)

        check_output('ml-git dataset checkout %s' % tag)

        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'cache')
        spec_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'dataset-ex.spec')
        file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile0')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_02_import_with_gdrive(self):
        cpath = 'credentials-json'
        init_repository("dataset", self)

        file_path_b = os.path.join("dataset-ex", "B")
        check_output(MLGIT_IMPORT % ("dataset", "mlgit", "dataset-ex")
                     + " --store-type=gdrive --object=B --credentials="+CREDENTIALS_PATH)

        self.assertTrue(os.path.exists(file_path_b))

        file_path = os.path.join("dataset-ex", "test-folder", "A")

        check_output(MLGIT_IMPORT % ("dataset", "mlgit", "dataset-ex")
                     + " --store-type=gdrive --path=test-folder --credentials=" + cpath)

        self.assertTrue(os.path.exists(file_path))