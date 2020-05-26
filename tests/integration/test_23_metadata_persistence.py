"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
import yaml

from tests.integration.commands import MLGIT_STATUS, MLGIT_ADD, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_INIT, MLGIT_REMOTE_ADD, \
    MLGIT_STORE_ADD, MLGIT_ENTITY_INIT, MLGIT_CHECKOUT, MLGIT_STORE_ADD_WITH_TYPE
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, BUCKET_NAME, PROFILE, STORE_TYPE
from tests.integration.helper import check_output, clear, init_repository
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class MetadataPersistenceTests(unittest.TestCase):

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_change_metadata(self):
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

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

        self.assertIn("No blobs", check_output(MLGIT_PUSH % ("dataset", "dataset-ex")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\nUntracked files:\n\nCorrupted files")

        clear(ML_GIT_DIR)
        clear("dataset")

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, "dataset"), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD_WITH_TYPE % (BUCKET_NAME, PROFILE, STORE_TYPE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(self.tmp_dir, ML_GIT_DIR, "dataset", "metadata")),
                      check_output(MLGIT_ENTITY_INIT % "dataset"))

        check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__17"))

        spec_file = os.path.join(self.tmp_dir, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        readme = os.path.join(self.tmp_dir, 'dataset', "computer-vision", "images", "dataset-ex", "README.md")

        with open(spec_file, "r") as f:
            spec = yaml.safe_load(f)
            self.assertEqual(spec["dataset"]["version"], 17)

        with open(readme, "r") as f:
            self.assertEqual(f.read(), "NEW2")
