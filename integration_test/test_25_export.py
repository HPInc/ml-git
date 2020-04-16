"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR, clean_git, PROFILE, BUCKET_NAME
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages


class ExportTagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_export_dataset_tag(self):

        self.export('dataset', 'dataset-ex')

    def test_02_export_model_tag(self):

        self.export('model', 'model-ex')

    def test_03_export_labels_tag(self):

        self.export('labels','labels-ex')

    def export(self, repotype, entity):
        clean_git()
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, repotype))
        init_repository(repotype, self)
        add_file(self, repotype, '--bumpversion', 'file')
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, repotype, 'metadata'),
                                      os.path.join('computer-vision', 'images', entity)),
                      check_output('ml-git %s commit %s' % (repotype, entity)))
        check_output('ml-git %s push %s' % (repotype, entity))
        store = "s3h://mlgit"
        tag = 'computer-vision__images__%s__12' % entity
        self.assertIn(messages[66] % (tag, store, "s3://mlgit"), check_output(MLGIT_EXPORT % (
        repotype, " {} {} --credentials={} --endpoint=http://127.0.0.1:9000".format(tag, BUCKET_NAME, PROFILE))))
        self.assertTrue(os.path.exists(os.path.join(PATH_TEST, "data", "mlgit", "filefile0")))
