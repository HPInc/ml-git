"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, clean_git, PROFILE, BUCKET_NAME
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages


class ExportTagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_export_tag(self):

        clean_git()

        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        add_file(self, 'dataset', '--bumpversion', 'file')

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output('ml-git dataset commit dataset-ex'))

        check_output('ml-git dataset push dataset-ex')
        store = "s3h://mlgit"

        tag = 'computer-vision__images__dataset-ex__12'

        self.assertIn(messages[74] % (tag, store, "s3://mlgit"), check_output("ml-git dataset export {} {} --credentials={} --endpoint=http://127.0.0.1:9000".format(tag, BUCKET_NAME, PROFILE)))
        self.assertTrue(os.path.exists(os.path.join(PATH_TEST, "data", "mlgit", "filefile0")))

