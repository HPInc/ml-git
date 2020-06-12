"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR
from integration_test.helper import check_output, clear, init_repository
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
