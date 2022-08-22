"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import unittest

import pytest

from ml_git.constants import LABELS_SPEC_KEY, DATASET_SPEC_KEY, MODEL_SPEC_KEY
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_GRAPH, MLGIT_ADD, MLGIT_COMMIT
from tests.integration.helper import check_output, init_repository, DATASETS, DATASET_NAME, ERROR_MESSAGE, ML_GIT_DIR, \
    LABELS, yaml_processor, MODELS


@pytest.mark.usefixtures('tmp_dir')
class GraphCommandsAcceptanceTests(unittest.TestCase):
    def create_file_in_ws(self, entity, name, value):
        with open(os.path.join(entity, entity + '-ex', name), 'wt') as z:
            z.write(value * 100)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_graph_command(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, 'file --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (LABELS, label_name, 'file --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (LABELS, label_name, '--dataset=dataset-ex')))
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (MODELS, model_name, 'file --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (MODELS, model_name, '')))

        self.create_file_in_ws(MODELS, 'file2', '2')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (MODELS, model_name, 'file2 --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (MODELS, model_name, '--dataset=dataset-ex --labels=labels-ex')))

        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_graph_with_empty_export_path(self):
        self.assertIn(output_messages['ERROR_EMPTY_VALUE'], check_output(MLGIT_GRAPH.format('--export-path=')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_graph_in_empty_directory(self):
        init_repository(DATASETS, self)
        output = check_output(MLGIT_GRAPH.format(''))
        self.assertEquals(1, output.count(output_messages['ERROR_NOT_IN_RESPOSITORY']))
