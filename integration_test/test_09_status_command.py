"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, init_repository
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_status_after_put_on_new_file_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        workspace = "dataset/dataset-ex"

        os.makedirs(workspace)

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 12
            }
        }

        with open(os.path.join(workspace, "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

            with open(os.path.join(workspace, 'file'), "wb") as z:
                z.write(b'0' * 1024)
        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+dataset-ex\.spec")

    def test_02_status_after_add_command_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        workspace = "dataset/dataset-ex"

        os.makedirs(workspace)

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 12
            }
        }

        with open(os.path.join(workspace, "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

            with open(os.path.join(workspace, 'file0'), "wb") as z:
                z.write(b'0' * 1024)

        self.assertIn(messages[13], check_output('ml-git dataset add dataset-ex --bumpversion'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: file0\s+untracked files")

    def test_03_status_after_commit_command_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        workspace = "dataset/dataset-ex"

        os.makedirs(workspace)

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 12
            }
        }

        with open(os.path.join(workspace, "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

            with open(os.path.join(workspace, 'file0'), "wb") as z:
                z.write(b'0' * 1024)

        self.assertIn(messages[13], check_output('ml-git dataset add dataset-ex --bumpversion --del'))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files")


    def test_04_status_after_checkout_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn("", check_output('ml-git dataset checkout computer-vision__images__dataset-ex__11'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+dataset-ex.spec")
