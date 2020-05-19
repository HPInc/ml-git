"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, create_spec, entity_init, create_file
from integration_test.helper import check_output, clear, init_repository, add_file, ERROR_MESSAGE
from integration_test.output_messages import messages
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import yaml
from integration_test.commands import *


class MutabilityAcceptanceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _create_entity_with_mutability(self, entity_type, mutability_type):
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        entity_init(entity_type, self)
        workspace = os.path.join(entity_type, entity_type + "-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, entity_type, PATH_TEST, 16, mutability_type)

        os.makedirs(os.path.join(workspace, "data"))

        create_file(workspace, "file1", "0")
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, entity_type+"-ex", "")))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + "-ex", "")))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+"-ex")))
        clear(ML_GIT_DIR)
        clear(workspace)
        clear(os.path.join(PATH_TEST, entity_type))

    def _checkout_entity(self, entity_type, tag="computer-vision__images__dataset-ex__16"):
        init_repository(entity_type, self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, entity_type, "metadata")),
                      check_output(MLGIT_UPDATE % entity_type))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity_type, tag)))

    def _verify_mutability(self, entity_type, mutability_type, spec_with_categories):
        with open(spec_with_categories) as y:
            ws_spec = yaml.load(y, Loader=yaml.SafeLoader)
            self.assertEqual(ws_spec[entity_type]["mutability"], mutability_type)
        return ws_spec

    def _change_mutability(self, entity_type, mutability_type, spec_with_categories, ws_spec):
        with open(spec_with_categories, "w") as y:
            ws_spec[entity_type]['mutability'] = mutability_type
            ws_spec[entity_type]['version'] = 17
            yaml.safe_dump(ws_spec, y)

    def test_01_mutability_strict_push(self):
        entity_type = "dataset"
        self._create_entity_with_mutability(entity_type, "strict")
        self._checkout_entity(entity_type)

        spec_with_categories = os.path.join(entity_type, "computer-vision", "images", entity_type + "-ex",
                                            entity_type + "-ex.spec")

        ws_spec = self._verify_mutability(entity_type, "strict", spec_with_categories)
        self._change_mutability(entity_type, "flexible", spec_with_categories, ws_spec)

        create_file(os.path.join(entity_type, "computer-vision", "images", entity_type+"-ex"), "file2", "012")

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+"-ex", "")))

    def test_02_mutability_flexible_push(self):
        entity_type = "model"
        self._create_entity_with_mutability(entity_type, "flexible")
        self._checkout_entity(entity_type, "computer-vision__images__model-ex__16")

        spec_with_categories = os.path.join(entity_type, "computer-vision", "images", entity_type + "-ex",
                                            entity_type + "-ex.spec")

        ws_spec = self._verify_mutability(entity_type, "flexible", spec_with_categories)
        self._change_mutability(entity_type, "strict", spec_with_categories, ws_spec)

        create_file(os.path.join(entity_type, "computer-vision", "images", entity_type+"-ex"), "file2", "012")

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+"-ex", "")))

    def test_03_mutability_mutable_push(self):
        entity_type = "labels"
        self._create_entity_with_mutability(entity_type, "mutable")
        self._checkout_entity(entity_type, "computer-vision__images__labels-ex__16")

        spec_with_categories = os.path.join(entity_type, "computer-vision", "images", entity_type + "-ex",
                                            entity_type + "-ex.spec")

        ws_spec = self._verify_mutability(entity_type, "mutable", spec_with_categories)
        self._change_mutability(entity_type, "strict", spec_with_categories, ws_spec)

        create_file(os.path.join(entity_type, "computer-vision", "images", entity_type+"-ex"), "file2", "012")

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+"-ex", "")))
