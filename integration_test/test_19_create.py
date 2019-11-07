"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR, IMPORT_PATH

from integration_test.output_messages import messages


class CreateAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_create(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'local_git_server.git', 'refs', 'tags'))
        init_repository('dataset', self)

        
        os.makedirs(IMPORT_PATH)

        self.assertIn(messages[38], check_output("ml-git dataset create data-ex --category=imgs --version-number=1 "
                                                 "--import=%s" % IMPORT_PATH))

        folderData = os.path.join(PATH_TEST, 'dataset', "data-ex", "data")
        spec = os.path.join(PATH_TEST, 'dataset', "data-ex", "data-ex.spec")
        readme = os.path.join(PATH_TEST, 'dataset', "data-ex", "README.md")

        self.assertTrue(os.path.exists(folderData))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

        clear(os.path.join(PATH_TEST, 'dataset', 'data-ex'))

        shutil.rmtree(IMPORT_PATH)
