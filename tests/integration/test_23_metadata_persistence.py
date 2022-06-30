"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.constants import STORAGE_SPEC_KEY, DATASET_SPEC_KEY
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_STATUS, MLGIT_ADD, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_INIT, \
    MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_CHECKOUT, MLGIT_STORAGE_ADD_WITH_TYPE
from tests.integration.helper import DATASET_ADD_INFO_REGEX, DATASET_NO_COMMITS_INFO_REGEX, ML_GIT_DIR, \
    GIT_PATH, BUCKET_NAME, PROFILE, STORAGE_TYPE, DATASETS, DATASET_NAME, STRICT, S3H, disable_wizard_in_config, \
    create_file, ERROR_MESSAGE
from tests.integration.helper import check_output, clear, init_repository, yaml_processor


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class MetadataPersistenceTests(unittest.TestCase):

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_change_metadata(self):
        init_repository(DATASETS, self)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'datasets-ex.spec')

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))

        readme = os.path.join(DATASETS, DATASET_NAME, 'README.md')

        with open(readme, 'w') as file:
            file.write('NEW')

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'New file: datasets-ex.spec\s+'
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'README.md')

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))

        status = check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME))

        self.assertIn('New file: datasets-ex.spec', status)
        self.assertIn('New file: README.md', status)

        with open(readme, 'w') as file:
            file.write('NEW2')

        spec = {
            DATASET_SPEC_KEY: {
                'categories': ['computer-vision', 'images'],
                'manifest': {
                    'files': 'MANIFEST.yaml',
                    STORAGE_SPEC_KEY: '%s://mlgit' % S3H
                },
                'mutability': STRICT,
                'name': 'datasets-ex',
                'version': 16
            }
        }

        with open(os.path.join(DATASETS, DATASET_NAME, 'datasets-ex.spec'), 'w') as y:
            spec[DATASET_SPEC_KEY]['version'] = 17
            yaml_processor.dump(spec, y)

        status = check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME))

        self.assertNotIn('new file: README.md', status)
        self.assertIn('README.md', status)
        self.assertNotIn('new file: datasets-ex.spec', status)
        self.assertIn('datasets-ex.spec', status)

        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        create_file(data_path, 'file', '0', '')

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ' --version=17')))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, DATASET_NAME)))

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX)

        clear(ML_GIT_DIR)
        clear(DATASETS)

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, DATASETS), check_output(MLGIT_REMOTE_ADD % (DATASETS, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD_WITH_TYPE % (BUCKET_NAME, PROFILE, STORAGE_TYPE)))
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (GIT_PATH, os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % DATASETS))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, 'computer-vision__images__datasets-ex__17 --bare')))

        spec_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'datasets-ex.spec')
        readme = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'README.md')

        with open(spec_file, 'r') as f:
            spec = yaml_processor.load(f)
            self.assertEqual(spec[DATASET_SPEC_KEY]['version'], 17)

        with open(readme, 'r') as f:
            self.assertEqual(f.read(), 'NEW2')
