"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, entity_init
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages


class TagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_add_tag(self):
        entity_init('dataset', self)

        add_file(self, 'dataset', '--bumpversion', 'new')

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output('ml-git dataset commit dataset-ex'))

        check_output('ml-git dataset push dataset-ex')

        with open(os.path.join('dataset', 'dataset' + "-ex", 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[53], check_output('ml-git dataset tag dataset-ex add test-tag'))

        check_output('ml-git dataset push dataset-ex')

        tag_file = os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags', 'test-tag')
        self.assertTrue(os.path.exists(tag_file))

    def test_02_add_tag_wrong_entity(self):
        entity_init('dataset', self)

        self.assertIn(messages[55] % 'dataset-wrong', check_output('ml-git dataset tag dataset-wrong add test-tag'))

    def test_03_add_tag_without_previous_commit(self):
        entity_init('dataset', self)

        self.assertIn(messages[48] % 'dataset-ex', check_output('ml-git dataset tag dataset-ex add test-tag'))

    def test_05_add_existing_tag(self):
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        entity_init('dataset', self)
        add_file(self, 'dataset', '--bumpversion', 'new')

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output('ml-git dataset commit dataset-ex'))

        check_output('ml-git dataset push dataset-ex')

        with open(os.path.join('dataset', 'dataset' + "-ex", 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        check_output('ml-git dataset tag dataset-ex add test-tag')

        check_output('ml-git dataset push dataset-ex')

        with open(os.path.join('dataset', 'dataset' + "-ex", 'file2'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[49] % 'test-tag', check_output('ml-git dataset tag dataset-ex add test-tag'))

    def test_06_add_tag_and_push(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        init_repository('dataset', self)
        metadata_path = os.path.join(ML_GIT_DIR, "dataset", "metadata")

        add_file(self, 'dataset', '--bumpversion', 'new')

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output('ml-git dataset commit dataset-ex'))

        check_output('ml-git dataset push dataset-ex')

        with open(os.path.join('dataset', 'dataset' + "-ex", 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[53], check_output('ml-git dataset tag dataset-ex add test-tag'))

        check_output('ml-git dataset push dataset-ex')
        os.chdir(metadata_path)
        self.assertTrue(os.path.exists(
            os.path.join(PATH_TEST, 'data', 'mlgit', 'zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12')))
        self.assertIn('test-tag', check_output('git describe --tags'))
