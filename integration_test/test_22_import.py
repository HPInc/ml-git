"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR, entity_init, CREDENTIALS_PATH
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages


class ImportAcceptanceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_import_with_wrong_credentials(self):
        clear(ML_GIT_DIR)
        init_repository("dataset", self)

        self.assertIn(messages[54], check_output(MLGIT_IMPORT % ("dataset", "bucket", "dataset-ex")
                                                 + " --credentials=personal"))

    def test_02_import_with_wrong_bucket(self):
        clear(ML_GIT_DIR)
        init_repository("dataset", self)

        self.assertIn(messages[51], check_output(MLGIT_IMPORT % ("dataset", "wrong-bucket", "dataset-ex")
                                                 + " --object=test  --credentials=minio"))

    def test_03_import_when_credentials_does_not_exist(self):
        clear(ML_GIT_DIR)
        init_repository("dataset", self)

        self.assertIn(messages[52] % "anyone", check_output(MLGIT_IMPORT % ("dataset", "bucket", "dataset-ex")
                                                            + " --credentials=anyone"))

    def test_04_import_with_gdrive(self):
        clear(ML_GIT_DIR)
        init_repository("dataset", self)

        file_path_b = os.path.join("dataset-ex", "B")
        check_output(MLGIT_IMPORT % ("dataset", "mlgit", "dataset-ex")
                     + " --store-type=gdrive --object=B --credentials="+CREDENTIALS_PATH)

        self.assertTrue(os.path.exists(file_path_b))

        file_path = os.path.join("dataset-ex", "test-folder", "A")

        check_output(MLGIT_IMPORT % ("dataset", "mlgit", "dataset-ex")
                     + " --store-type=gdrive --path=test-folder --credentials=" + CREDENTIALS_PATH)

        self.assertTrue(os.path.exists(file_path))