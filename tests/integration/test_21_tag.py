"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_TAG_ADD
from tests.integration.helper import PATH_TEST, ML_GIT_DIR, create_file, ERROR_MESSAGE
from tests.integration.helper import check_output, init_repository, add_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class TagAcceptanceTests(unittest.TestCase):

    def set_up_tag(self, entity_type):
        init_repository(entity_type, self)

    def _add_tag_entity(self, entity_type):
        self.set_up_tag(entity_type)

        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+"-ex")))

        with open(os.path.join(entity_type, entity_type + "-ex", 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[53], check_output(MLGIT_TAG_ADD % (entity_type, entity_type+"-ex", "test-tag")))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+"-ex")))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_01_add_tag(self):
        self._add_tag_entity("dataset")

        tag_file = os.path.join(self.tmp_dir, "local_git_server.git", "refs", "tags", "test-tag")
        self.assertTrue(os.path.exists(tag_file))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_02_add_tag_wrong_entity(self):
        self.set_up_tag("dataset")

        self.assertIn(messages[55] % "dataset-wrong", check_output(MLGIT_TAG_ADD
                                                                   % ("dataset", "dataset-wrong", "test-tag")))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_03_add_tag_without_previous_commit(self):
        self.set_up_tag("dataset")

        self.assertIn(messages[48] % "dataset-ex", check_output(MLGIT_TAG_ADD % ("dataset", "dataset-ex", "test-tag")))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_04_add_existing_tag(self):
        self._add_tag_entity("dataset")

        create_file(os.path.join("dataset", "dataset" + "-ex"), "file2", "0", "")

        tag_file = os.path.join(self.tmp_dir, "local_git_server.git", "refs", "tags", "test-tag")
        self.assertTrue(os.path.exists(tag_file))

        self.assertIn(messages[49] % "test-tag", check_output(MLGIT_TAG_ADD % ("dataset", "dataset-ex", "test-tag")))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_05_add_tag_and_push(self):
        self._add_tag_entity("dataset")
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, "dataset", "metadata")
        os.chdir(metadata_path)

        self.assertTrue(os.path.exists(os.path.join(PATH_TEST, "data", "mlgit",
                                                    "zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12")))
        self.assertIn("test-tag", check_output("git describe --tags"))
