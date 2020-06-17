"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import sys
import unittest

import pytest

from tests.integration.commands import MLGIT_CHECKOUT, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_STORE_ADD
from tests.integration.helper import ML_GIT_DIR, MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_ADD, \
    recursive_write_read, ERROR_MESSAGE, \
    add_file, GIT_PATH, check_output, clear, init_repository, BUCKET_NAME, PROFILE, edit_config_yaml, \
    create_spec, set_write_read, STORE_TYPE
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class CheckoutTagAcceptanceTests(unittest.TestCase):

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(messages[17] % (metadata_path, os.path.join('computer-vision', 'images', entity + '-ex')),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(messages[8] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_checkout_tag(self):
        self.set_up_checkout('dataset')
        check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1'))
        file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile0')
        self.check_metadata()
        self.check_amount_of_files('dataset', 6)
        self.assertTrue(os.path.exists(file))

    def check_metadata(self):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'cache')
        spec_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'dataset-ex.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_checkout_with_group_sample(self):
        self.set_up_checkout('dataset')
        check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1 --sample-type=group '
                                                  '--sampling=2:4 --seed=5'))
        self.check_metadata()
        self.check_amount_of_files('dataset', 3)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_group_sample_with_amount_parameter_greater_than_group_size(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[21], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=4:2 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_group_sample_with_amount_parameter_equal_to_group_size(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[21], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=2:2 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_group_sample_with_group_size_parameter_greater_than_list_size(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[22], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=2:30 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_group_sample_with_group_size_parameter_less_than_zero(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[41], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=-2:3 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_checkout_with_range_sample(self):
        self.set_up_checkout('dataset')
        self.assertIn('', check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                       + ' --sample-type=range --sampling=2:4:1'))
        self.check_metadata()
        self.check_amount_of_files('dataset', 3)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_range_sample_with_start_parameter_greater_than_stop(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=range --sampling=4:2:1'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_range_sample_with_start_parameter_less_than_zero(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=range --sampling=3:2:1'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_10_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[26], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=range --sampling=1:3:4'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_11_range_sample_with_start_parameter_equal_to_stop(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=range --sampling=2:2:1'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_12_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[24], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=range --sampling=2:30:1'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_13_checkout_with_random_sample(self):
        self.set_up_checkout('dataset')

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                     + ' --sample-type=random --sampling=2:3 --seed=3'))
        self.check_amount_of_files('dataset', 4)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_14_random_sample_with_frequency_less_or_equal_zero(self):
        self.set_up_checkout('dataset')

        self.assertIn(messages[30], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=random --sampling=2:2 --seed=3'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_15_random_sample_with_amount_parameter_greater_than_frequency(self):
        self.set_up_checkout('dataset')

        self.assertIn(messages[30], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=random --sampling=4:2 --seed=3'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_16_random_sample_with_frequency_greater_or_equal_list_size(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[31], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=random --sampling=2:10 --seed=3'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_17_random_sample_with_frequency_equal_zero(self):
        self.set_up_checkout('dataset')

        self.assertIn(messages[29], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=random --sampling=2:0 --seed=3'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_18_group_sample_with_group_size_parameter_equal_zero(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[28], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=1:0 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_19_group_sample_with_amount_parameter_equal_zero(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[43], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')
                                                 + ' --sample-type=group --sampling=0:1 --seed=5'))
        self.check_amount_of_files('dataset', 0)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_20_model_related(self):
        model = 'model'
        dataset = 'dataset'
        labels = 'labels'
        git_server = os.path.join(self.tmp_dir, GIT_PATH)

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (git_server, model), check_output(MLGIT_REMOTE_ADD % (model, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(self.tmp_dir, '.ml-git', model, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % 'model'))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_model = os.path.join(model, model + '-ex')
        os.makedirs(workspace_model)
        version = 1
        create_spec(self, model, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_model, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[2] % (git_server, dataset), check_output(MLGIT_REMOTE_ADD % (dataset, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(self.tmp_dir, '.ml-git', dataset, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % 'dataset'))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_dataset = os.path.join(dataset, dataset + '-ex')
        os.makedirs(workspace_dataset)
        version = 1
        create_spec(self, dataset, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_dataset, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[13] % 'dataset', check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, '.ml-git', 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ('dataset', 'dataset-ex')))

        self.assertIn(messages[2] % (git_server, labels), check_output(MLGIT_REMOTE_ADD % (labels, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(self.tmp_dir, '.ml-git', labels, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % labels))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_labels = os.path.join(labels, labels + '-ex')
        os.makedirs(workspace_labels)
        version = 1
        create_spec(self, labels, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_labels, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[15], check_output(MLGIT_ADD % ('labels', 'labels-ex', '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, '.ml-git', 'labels', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output(MLGIT_COMMIT % ('labels', 'labels-ex', '')))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ('labels', 'labels-ex')))

        self.assertIn(messages[14], check_output(MLGIT_ADD % ('model', 'model-ex', '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, '.ml-git', 'model', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output(MLGIT_COMMIT % ('model', 'model-ex', '--dataset=dataset-ex') + ' --labels=labels-ex'))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ('model', 'model-ex')))
        set_write_read(os.path.join(self.tmp_dir, workspace_model, 'file1'))
        set_write_read(os.path.join(self.tmp_dir, workspace_dataset, 'file1'))
        set_write_read(os.path.join(self.tmp_dir, workspace_labels, 'file1'))
        if not sys.platform.startswith('linux'):
            recursive_write_read(os.path.join(self.tmp_dir, '.ml-git'))
        clear(os.path.join(self.tmp_dir, model))
        clear(os.path.join(self.tmp_dir, dataset))
        clear(os.path.join(self.tmp_dir, labels))
        clear(os.path.join(self.tmp_dir, '.ml-git', model))
        clear(os.path.join(self.tmp_dir, '.ml-git', dataset))
        clear(os.path.join(self.tmp_dir, '.ml-git', labels))
        self.assertIn(messages[8] % (git_server, os.path.join(self.tmp_dir, '.ml-git', model, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % model))
        self.assertIn('', check_output(MLGIT_CHECKOUT % ('model', 'computer-vision__images__model-ex__2')
                                       + ' -d -l'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, model)))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, dataset)))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, labels)))
