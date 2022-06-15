"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import sys
import unittest

import pytest

from ml_git.constants import MLGIT_IGNORE_FILE_NAME
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CHECKOUT, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_STORAGE_ADD
from tests.integration.helper import ML_GIT_DIR, MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_ADD, \
    recursive_write_read, ERROR_MESSAGE, \
    add_file, GIT_PATH, check_output, clear, init_repository, BUCKET_NAME, PROFILE, edit_config_yaml, \
    create_spec, set_write_read, STORAGE_TYPE, create_file, populate_entity_with_new_data, DATASETS, DATASET_NAME, \
    MODELS, \
    LABELS, DATASET_TAG, create_ignore_file, disable_wizard_in_config


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class CheckoutTagAcceptanceTests(unittest.TestCase):
    entity_path = os.path.join(DATASETS, 'computer_vision', 'images', 'dataset-ex')

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity + '-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_path))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    def check_amount_of_files(self, entity_type, expected_files, sampling=True):
        entity_dir = os.path.join(self.tmp_dir, entity_type, entity_type+'-ex')
        if expected_files == 0:
            self.assertFalse(os.path.exists(entity_dir))
            self.assertFalse(self.check_sampling_flag(DATASETS))
            return
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)
        if sampling:
            self.assertTrue(self.check_sampling_flag(DATASETS))

    def check_sampling_flag(self, entity):
        sampling = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'index', 'metadata', entity+'-ex', 'sampling')
        return os.path.exists(sampling)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_checkout_tag(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 6
        check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace, sampling=False)
        self.assertTrue(os.path.exists(file))

    def check_metadata(self, artifact_name=DATASET_NAME):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, artifact_name, artifact_name+'.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_checkout_with_group_sample(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 3
        check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG + ' --sample-type=group --sampling=2:4 --seed=5'))
        self.check_metadata()
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)
        self.assertTrue(self.check_sampling_flag(DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_group_sample_with_amount_parameter_greater_than_group_size(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_GROUP_SIZE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=4:2 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_group_sample_with_amount_parameter_equal_to_group_size(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_GROUP_SIZE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=2:2 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_group_sample_with_group_size_parameter_greater_than_list_size(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_GROUP_SIZE_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=2:30 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_group_sample_with_group_size_parameter_less_than_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_AMOUNT_GROUP_REQUIRES_POSITIVE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=-2:3 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_checkout_with_range_sample(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 3
        self.assertIn('', check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)
                                       + ' --sample-type=range --sampling=2:4:1'))
        self.check_metadata()
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_range_sample_with_start_parameter_greater_than_stop(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=4:2:1'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_range_sample_with_start_parameter_less_than_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=3:2:1'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_10_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_STEP_PARAMETER_SHOULD_BE_SMALLER_STOP'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=1:3:4'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_11_range_sample_with_start_parameter_equal_to_stop(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=2:2:1'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_12_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0
        self.assertIn(output_messages['ERROR_STOP_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=2:30:1'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_13_checkout_with_random_sample(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 4

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=random --sampling=2:3 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_14_random_sample_with_frequency_less_or_equal_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_FREQUENCY'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=2:2 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_15_random_sample_with_amount_parameter_greater_than_frequency(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_FREQUENCY'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=4:2 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_16_random_sample_with_frequency_greater_or_equal_list_size(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_FREQUENCY_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=2:10 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_17_random_sample_with_frequency_equal_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_FREQUENCY_PARAMETER_SHOULD_BE_GREATER_ZERO'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=2:0 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_18_group_sample_with_group_size_parameter_equal_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_GROUP_SIZE_PARAMETER_SHOULD_BE_GREATER_ZERO'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=1:0 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_19_group_sample_with_amount_parameter_equal_zero(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 0

        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_GREATER_ZERO'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=0:1 --seed=5'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_20_model_related(self):
        git_server = os.path.join(self.tmp_dir, GIT_PATH)

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (git_server, MODELS), check_output(MLGIT_REMOTE_ADD % (MODELS, git_server)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (git_server, os.path.join(self.tmp_dir, '.ml-git', MODELS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % MODELS))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_model = os.path.join(MODELS, MODELS + '-ex')
        os.makedirs(workspace_model)
        version = 1
        create_spec(self, MODELS, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_model, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (git_server, DATASETS), check_output(MLGIT_REMOTE_ADD % (DATASETS, git_server)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (git_server, os.path.join(self.tmp_dir, '.ml-git', DATASETS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % DATASETS))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_dataset = os.path.join(DATASETS, DATASETS + '-ex')
        os.makedirs(workspace_dataset)
        version = 1
        create_spec(self, DATASETS, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_dataset, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        expected_push_result = '2.00/2.00'

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, '.ml-git', DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        self.assertIn(expected_push_result, check_output(MLGIT_PUSH % (DATASETS, DATASET_NAME)))

        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (git_server, LABELS), check_output(MLGIT_REMOTE_ADD % (LABELS, git_server)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (git_server, os.path.join(self.tmp_dir, '.ml-git', LABELS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % LABELS))
        edit_config_yaml(os.path.join(self.tmp_dir, '.ml-git'))
        workspace_labels = os.path.join(LABELS, LABELS + '-ex')
        os.makedirs(workspace_labels)
        version = 1
        create_spec(self, LABELS, self.tmp_dir, version)
        with open(os.path.join(self.tmp_dir, workspace_labels, 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(output_messages['INFO_ADDING_PATH'] % LABELS, check_output(MLGIT_ADD % (LABELS, LABELS+'-ex', '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, '.ml-git', LABELS, 'metadata'), LABELS+'-ex'),
                      check_output(MLGIT_COMMIT % (LABELS, LABELS+'-ex', '')))
        self.assertIn(expected_push_result, check_output(MLGIT_PUSH % (LABELS, LABELS+'-ex')))

        self.assertIn(output_messages['INFO_ADDING_PATH'] % MODELS, check_output(MLGIT_ADD % (MODELS, MODELS+'-ex', '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, '.ml-git', MODELS, 'metadata'), MODELS+'-ex'),
                      check_output(
                          MLGIT_COMMIT % (MODELS, MODELS+'-ex', '--dataset=datasets-ex') + ' --labels=labels-ex'))
        self.assertIn(expected_push_result, check_output(MLGIT_PUSH % (MODELS, MODELS+'-ex')))
        set_write_read(os.path.join(self.tmp_dir, workspace_model, 'file1'))
        set_write_read(os.path.join(self.tmp_dir, workspace_dataset, 'file1'))
        set_write_read(os.path.join(self.tmp_dir, workspace_labels, 'file1'))
        if not sys.platform.startswith('linux'):
            recursive_write_read(os.path.join(self.tmp_dir, '.ml-git'))
        clear(os.path.join(self.tmp_dir, MODELS))
        clear(os.path.join(self.tmp_dir, DATASETS))
        clear(os.path.join(self.tmp_dir, LABELS))
        clear(os.path.join(self.tmp_dir, '.ml-git', MODELS))
        clear(os.path.join(self.tmp_dir, '.ml-git', DATASETS))
        clear(os.path.join(self.tmp_dir, '.ml-git', LABELS))
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (git_server, os.path.join(self.tmp_dir, '.ml-git', MODELS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % MODELS))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (MODELS, 'computer-vision__images__models-ex__1')
                                                     + ' -d -l'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, MODELS)))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, DATASETS)))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, LABELS)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_21_check_error_for_checkout_sample_with_labels(self):
        self.set_up_checkout(LABELS)
        output = check_output(MLGIT_CHECKOUT % (LABELS, 'computer-vision__images__labels-ex__1 --sample-type=group '
                                                        '--sampling=2:4 --seed=5'))

        self.assertIn(output_messages['ERROR_NO_SUCH_OPTION'] % '--sample-type', output)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, LABELS)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_22_check_error_for_checkout_sample_with_model(self):
        self.set_up_checkout(MODELS)
        output = check_output(MLGIT_CHECKOUT % (MODELS, 'computer-vision__images__models-ex__1 --sample-type=group '
                                                        '--sampling=2:4 --seed=5'))

        self.assertIn(output_messages['ERROR_NO_SUCH_OPTION'] % '--sample-type', output)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, MODELS)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_23_add_after_checkout_with_sample(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 4
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=random --sampling=2:3 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        create_file(workspace, 'new_file', '0', file_path='')
        self.assertIn(output_messages['INFO_CANNOT_ADD_NEW_DATA_AN_ENTITY'], check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_24_check_sampling_flag_after_checkout(self):
        entity = DATASETS
        self.set_up_checkout(entity)
        number_of_files_in_workspace = 4
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, DATASET_TAG)))
        workspace = os.path.join(self.tmp_dir, entity, entity+'-ex')
        create_file(workspace, 'new_file', '0', file_path='')
        populate_entity_with_new_data(self, entity)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=random --sampling=2:3 --seed=3'))
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, 'computer-vision__images__datasets-ex__2')))
        self.assertFalse(self.check_sampling_flag(DATASETS))

    @pytest.mark.usefixtures('start_local_git_server_with_main_branch', 'switch_to_tmp_dir')
    def test_25_checkout_tag_with_main_branch(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 6
        check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace, sampling=False)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_26_adding_data_based_in_older_tag(self):
        entity = DATASETS
        self.set_up_checkout(entity)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, DATASET_TAG)))
        workspace = os.path.join(self.tmp_dir, entity, entity+'-ex')
        create_file(workspace, 'newfile5', '0', file_path='')
        populate_entity_with_new_data(self, entity)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        expected_files_in_tag_1 = 6
        self.check_amount_of_files(entity, expected_files_in_tag_1, sampling=False)
        create_file(workspace, 'newfile6', '0', file_path='')
        populate_entity_with_new_data(self, entity, bumpversion='', version='--version=3')

        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, 'computer-vision__images__datasets-ex__3')))

        path_of_tag_2_file = os.path.join(self.tmp_dir, entity, entity+'-ex', 'newfile5')
        path_of_tag_3_file = os.path.join(self.tmp_dir, entity, entity+'-ex', 'newfile6')
        self.assertFalse(os.path.exists(path_of_tag_2_file))
        self.assertTrue(os.path.exists(path_of_tag_3_file))
        expected_files_in_tag_3 = 7
        self.check_amount_of_files(entity, expected_files_in_tag_3, sampling=False)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_27_checkout_tag_with_fail_limit(self):
        self.set_up_checkout(DATASETS)
        number_of_files_in_workspace = 6
        output = check_output(MLGIT_CHECKOUT % (DATASETS, '{} {}'.format(DATASET_TAG, ' --fail-limit=20')))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, number_of_files_in_workspace, sampling=False)
        self.assertTrue(os.path.exists(file))
        self.assertNotIn('Failed', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_28_checkout_entity_with_ignore_file(self):
        entity = DATASETS
        init_repository(entity, self)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.mkdir(os.path.join(workspace, 'data'))
        create_file(workspace, 'image.png', '0')
        create_file(workspace, 'file1', '0')
        create_ignore_file(workspace)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, DATASET_NAME)))

        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)

        mlgit_ignore_file_path = os.path.join(workspace, MLGIT_IGNORE_FILE_NAME)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % entity))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, DATASET_NAME)))

        self.assertTrue(os.path.exists(mlgit_ignore_file_path))
        self.assertTrue(os.path.exists(os.path.join(workspace, 'data', 'file1')))
        self.assertFalse(os.path.exists(os.path.join(workspace, 'data', 'image.png')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_29_checkout_entity_with_underscore_in_name(self):
        entity = DATASETS
        artifact_name = 'dataset_ex'
        tag = 'computer-vision__images__dataset_ex__1'
        init_repository(entity, self, artifact_name=artifact_name)
        add_file(self, entity, '', 'new', artifact_name=artifact_name)
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, artifact_name),
                      check_output(MLGIT_COMMIT % (entity, artifact_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, artifact_name)))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

        check_output(MLGIT_CHECKOUT % (DATASETS, tag))
        self.check_metadata(artifact_name=artifact_name)
