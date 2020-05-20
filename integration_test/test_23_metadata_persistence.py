"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import yaml

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR, clean_git, GIT_PATH, BUCKET_NAME, PROFILE, STORE_TYPE
from integration_test.helper import check_output, clear, init_repository
from integration_test.output_messages import messages


class MetadataPersistenceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_change_metadata(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository("dataset", self)
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\nUntracked files:\n\tdataset-ex.spec\n\nCorrupted files")

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "")))

        readme = os.path.join("dataset", "dataset-ex", "README.md")

        with open(readme, "w") as file:
            file.write("NEW")

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\tREADME.md\n\nCorrupted files")

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "")))

        status = check_output(MLGIT_STATUS % ("dataset", "dataset-ex"))

        self.assertIn("New file: dataset-ex.spec", status)
        self.assertIn("New file: README.md", status)

        with open(readme, "w") as file:
            file.write("NEW2")

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "mutability": "strict",
                "name": "dataset-ex",
                "version": 16
            }
        }

        with open(os.path.join("dataset", "dataset-ex", "dataset-ex.spec"), "w") as y:
            spec['dataset']['version'] = 17
            yaml.safe_dump(spec, y)

        status = check_output(MLGIT_STATUS % ("dataset", "dataset-ex"))

        self.assertNotIn("new file: README.md", status)
        self.assertIn("README.md", status)
        self.assertNotIn("new file: dataset-ex.spec", status)
        self.assertIn("dataset-ex.spec", status)

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "")))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

        self.assertIn("No blobs", check_output(MLGIT_PUSH % ("dataset", "dataset-ex")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\nUntracked files:\n\nCorrupted files")

        clear(ML_GIT_DIR)
        clear("dataset")

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, "dataset"), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output('ml-git repository store add %s --type=%s --credentials=%s'
                                   % (BUCKET_NAME, STORE_TYPE, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output(MLGIT_ENTITY_INIT % "dataset"))

        check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__17"))

        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        readme = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "README.md")

        with open(spec_file, "r") as f:
            spec = yaml.safe_load(f)
            self.assertEqual(spec["dataset"]["version"], 17)

        with open(readme, "r") as f:
            self.assertEqual(f.read(), "NEW2")
