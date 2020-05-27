"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_EXPORT
from tests.integration.helper import ML_GIT_DIR, PROFILE, BUCKET_NAME, \
    check_output, init_repository, add_file, PATH_TEST
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class ExportTagAcceptanceTests(unittest.TestCase):

    def export(self, repotype, entity):
        init_repository(repotype, self)
        add_file(self, repotype, '', repotype)
        file_in_store = os.path.join(PATH_TEST, 'data', 'mlgit', repotype+'file0')
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, repotype, 'metadata'),
                                      os.path.join('computer-vision', 'images', entity)),
                      check_output(MLGIT_COMMIT % (repotype, entity, '')))

        self.assertFalse(os.path.exists(file_in_store))

        check_output(MLGIT_PUSH % (repotype, entity))
        store = 's3h://mlgit'
        tag = 'computer-vision__images__%s__1' % entity
        self.assertIn(messages[66] % (tag, store, 's3://mlgit'), check_output(MLGIT_EXPORT % (
            repotype, ' {} {} --credentials={} --endpoint=http://127.0.0.1:9000'.format(tag, BUCKET_NAME, PROFILE))))

        self.assertTrue(os.path.exists(file_in_store))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_export_dataset_tag(self):

        self.export('dataset', 'dataset-ex')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_export_model_tag(self):

        self.export('model', 'model-ex')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_export_labels_tag(self):
        self.export('labels', 'labels-ex')
