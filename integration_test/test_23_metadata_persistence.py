"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import yaml

from integration_test.helper import PATH_TEST, ML_GIT_DIR, clean_git, GIT_PATH, BUCKET_NAME, PROFILE
from integration_test.helper import check_output, clear, init_repository
from integration_test.output_messages import messages


class MetadataPersistenceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_change_metadata(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)
        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+dataset-ex.spec")

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex"))

        readme = os.path.join("dataset","dataset-ex","README.md")

        with open(readme,"w") as file:
            file.write("NEW")

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+README.md")

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex"))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+")

        with open(readme,"w") as file:
            file.write("NEW2")

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 1
            }
        }

        with open(os.path.join("dataset", "dataset-ex", "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+dataset-ex.spec\s+README.md")

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex"))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertIn("No blobs", check_output("ml-git dataset push dataset-ex"))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+")

        clear(ML_GIT_DIR)
        clear("dataset")

        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output('ml-git dataset init'))

        check_output("ml-git dataset checkout computer-vision__images__dataset-ex__1")

        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")

        with open(spec_file, "r") as f:
            spec = yaml.safe_load(f)
            self.assertEqual(spec["dataset"]["version"], 1)





