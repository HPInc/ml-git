"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import git
import shutil
from integration_test.helper import check_output, clear, init_repository, BUCKET_NAME, PROFILE, add_file, \
    edit_config_yaml, create_spec, set_write_read, recursiva_write_read, entity_init, create_file, clean_git
from integration_test.helper import PATH_TEST, ML_GIT_DIR, ERROR_MESSAGE
import time


from integration_test.output_messages import messages


class CheckoutTagAcceptanceTests(unittest.TestCase):
    MLGIT_CHECKOUT = 'ml-git %s checkout %s %s'
    MLGIT_UPDATE = 'ml-git %s update'
    MLGIT_ADD = 'ml-git %s add %s %s'
    MLGIT_PUSH = 'ml-git %s push %s'
    MLGIT_COMMIT = 'ml-git %s commit %s %s'
    file = os.path.join(PATH_TEST, "dataset", "computer-vision", "images", "dataset-ex", "data", "file1")

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _push_files(self, entity_type, bumpversion="--bumpversion"):
        self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_ADD % (entity_type, entity_type+"-ex", bumpversion)))
        self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_COMMIT % (entity_type, entity_type + "-ex", "")))
        self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_PUSH % (entity_type, entity_type+"-ex")))

    def _clear_path(self, entity_type="dataset"):
        clear(ML_GIT_DIR)
        workspace = os.path.join(entity_type, entity_type + "-ex")
        clear(os.path.join(ML_GIT_DIR, entity_type, "cache"))
        clear(workspace)
        clear(os.path.join(PATH_TEST, entity_type))

    def _create_entity_with_mutability(self, entity_type, mutability_type):
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        entity_init(entity_type, self)
        workspace = os.path.join(entity_type, entity_type + "-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, entity_type, PATH_TEST, 16, mutability_type)

        os.makedirs(os.path.join(workspace, "data"))
        create_file(workspace, "file1", "0")

        self._push_files(entity_type, "")
        self._clear_path()

    def _checkout_entity(self, entity_type, tag="computer-vision__images__dataset-ex__16", bare=True):
        init_repository(entity_type, self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, entity_type, "metadata")),
                      check_output(self.MLGIT_UPDATE % entity_type))
        if bare:
            self.assertIn(messages[76], check_output(self.MLGIT_CHECKOUT % (entity_type, tag, " --bare")))
        else:
            self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_CHECKOUT % (entity_type, tag, "")))
            self.assertTrue(os.path.exists(self.file))

    def check_bare_checkout(self, entity):
        objects = os.path.join(ML_GIT_DIR, entity, "objects")
        refs = os.path.join(ML_GIT_DIR, entity, "refs")
        cache = os.path.join(ML_GIT_DIR, entity, "cache")
        bare = os.path.join(ML_GIT_DIR, entity, "index", "metadata", entity+"-ex", "bare")
        spec_file = os.path.join(PATH_TEST, entity, "computer-vision", "images", entity+"-ex", entity+"-ex.spec")

        self.assertFalse(os.path.exists(cache))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(bare))
        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(spec_file))

    def test_01_checkout_bare(self):
        entity_type = "dataset"
        self._create_entity_with_mutability(entity_type, "strict")
        self._checkout_entity(entity_type)

        self.assertFalse(os.path.exists(self.file))

        self.check_bare_checkout(entity_type)

        self._clear_path()

    def test_02_push_file(self):
        entity_type = "dataset"
        self._checkout_entity(entity_type)
        self.assertFalse(os.path.exists(self.file))
        self.check_bare_checkout(entity_type)

        data_path = os.path.join(entity_type, "computer-vision", "images", entity_type+"-ex")
        os.mkdir(os.path.join(data_path, "data"))
        create_file(data_path, "file2", "1")

        self._push_files(entity_type)
        self._clear_path()

        self._checkout_entity(entity_type, tag="computer-vision__images__"+entity_type+"-ex__17", bare=False)

        file2 = os.path.join(PATH_TEST, entity_type, "computer-vision", "images", entity_type+"-ex", "data", "file2")
        self.assertTrue(os.path.exists(self.file))
        self.assertTrue(os.path.exists(file2))

        self._clear_path()

    def _create_file_with_same_path(self, entity_type="dataset"):
        entity_path = os.path.join(PATH_TEST, entity_type, "computer-vision", "images", entity_type+"-ex")

        file = os.path.join(entity_path, "data", "file1")
        self.assertFalse(os.path.exists(file))

        os.mkdir(os.path.join(entity_path, "data"))
        create_file(entity_path, "file1", "1")
        self.assertTrue(os.path.exists(file))

    def test_03_push_file_with_same_path_strict(self):
        entity_type = "dataset"
        self._create_entity_with_mutability(entity_type, "strict")
        self._checkout_entity(entity_type)
        self.check_bare_checkout(entity_type)

        self._create_file_with_same_path()
        self._push_files(entity_type)

        self._clear_path()

        self.assertFalse(os.path.exists(self.file))
        self._checkout_entity(entity_type, tag="computer-vision__images__"+entity_type+"-ex__17", bare=False)

        with open(self.file) as f:
            file_text = f.read()
            self.assertNotIn('1', file_text)
            self.assertIn('0', file_text)

        self._clear_path()

    def test_04_push_file_with_same_path_mutable(self):
        clean_git()
        entity_type = "dataset"
        self._create_entity_with_mutability(entity_type, "mutable")
        self._checkout_entity(entity_type)

        self.check_bare_checkout(entity_type)

        self._create_file_with_same_path()

        self.assertIn(messages[77] % "data/file1", check_output(self.MLGIT_ADD %
                                                                (entity_type, entity_type + "-ex", "--bumpversion")))
        self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_COMMIT % (entity_type, entity_type + "-ex", "")))
        self.assertNotIn(ERROR_MESSAGE, check_output(self.MLGIT_PUSH % (entity_type, entity_type + "-ex")))

        self._clear_path()

        self._checkout_entity(entity_type, tag="computer-vision__images__"+entity_type+"-ex__17", bare=False)

        with open(self.file) as f:
            file_text = f.read()
            self.assertNotIn('0', file_text)
            self.assertIn('1', file_text)

        self._clear_path()
