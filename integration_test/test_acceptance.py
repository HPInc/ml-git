"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR, GIT_PATH,\
    GIT_WRONG_REP, BUCKET_NAME, PROFILE

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    # Check the result of  "init" command
    def test_1_init(self):
        clear(ML_GIT_DIR)
        # assertion: 1 - Run the command in the project root directory

        self.assertIn(messages[0],check_output("ml-git init"))

        config = os.path.join(ML_GIT_DIR, "config.yaml")

        self.assertTrue(os.path.exists(config))

        # assertion: 2 - run the command in a project subfolder
        os.chdir(".ml-git")

        self.assertIn(messages[1],check_output("ml-git init"))

        # assertion: 3 - Attempt to initialize an already initialized repository
        os.chdir(PATH_TEST)

        self.assertIn(messages[1],check_output("ml-git init"))

    # Add a remote to dataset/labels/model entity
    def test_2_add_remote(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))

        # assertion: 1 - Run the command  to DATASET
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["dataset"]["git"])

        # assertion: 2 - Run the command  to LABELS
        self.assertIn(messages[3] % GIT_PATH,check_output('ml-git labels remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["labels"]["git"])

        # assertion: 3 - Run the command  to MODEL
        self.assertIn(messages[4] % GIT_PATH,check_output('ml-git model remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["model"]["git"])

        # assertion: 4 - Type the command from a different place of the project root
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))

        os.chdir(PATH_TEST)

        clear(ML_GIT_DIR)

        # assertion: 5 - Add remote to an uninitialized directory
        self.assertIn(messages[6],check_output('ml-git dataset remote add "%s"' % GIT_PATH))

        # assertion: 5 - Change remote repository
        self.assertIn(messages[0],check_output("ml-git init"))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[5] % (GIT_PATH, GIT_PATH),check_output('ml-git dataset remote add "%s"' % GIT_PATH))

    def test_3_add_store(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))

        # assertion: 1 - Run the command in the project root directory
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual("default", config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])

        # assertion: 2 - Add the same store again
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

        os.chdir(ML_GIT_DIR)

        # assertion: 3 - Type the command from a different place of the project root
        self.assertIn( messages[7] % (BUCKET_NAME, PROFILE),check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

        # assertion: 4 - Add store to an uninitialized directory
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[6],check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

    def test_4_init_dataset(self):
        clear(ML_GIT_DIR)
        # assertion: 1 - Run the command  to DATASET
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn( messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))

        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

        # assertion: 2 - Initialize twice the entity
        self.assertIn(messages[9] % os.path.join(ML_GIT_DIR, "dataset", "metadata"),check_output("ml-git dataset init"))

        clear(ML_GIT_DIR)

        # assertion: 3 - Type the command from a subfolder of the project root
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))

        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

        # assertion: 4 - Try to init with a wrong remote repository
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)

        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_WRONG_REP,check_output('ml-git dataset remote add %s' % GIT_WRONG_REP))

        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))

        self.assertIn(messages[10] % GIT_WRONG_REP, check_output("ml-git dataset init"))

        # assertion:5 - Try to init without configuring remote and storage
        clear(ML_GIT_DIR)

        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[11],check_output("ml-git dataset init"))

        # assertion: 6 - Run the command  to LABELS
        self.assertIn(messages[3] % GIT_PATH,check_output('ml-git labels remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "labels", "metadata")),check_output("ml-git labels init"))

        # assertion: 7 - Run the command  to MODEL
        self.assertIn(messages[4] % GIT_PATH,check_output('ml-git model remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "model", "metadata")),check_output("ml-git model init"))

    def test_5_add_files(self):

        # Assertion 1: - Run the command  to DATASET
        clear(ML_GIT_DIR)
        add_file('dataset', '', self)

        # Assertion 2: - Run the command  to MODEL
        clear(ML_GIT_DIR)
        add_file('model', '', self)

        # Assertion 3: - Run the command  to LABELS
        clear(ML_GIT_DIR)
        add_file('labels', '', self)

        # Assertion 4: - Run add command with a nonexistent dataset
        # Assertion 5 - Add without any repository changes

        # Assertion 6 - Run the command with parameter (--bumpversion)
        clear(ML_GIT_DIR)
        add_file('dataset', '--bumpversion', self)

        # Assertion: 7 - Run the ADD command  to DATASET  without --bumpversion



"""
    # Commit executation example
    def test_6_commit_files(self):

        # Create assert to ml-git commit and messages
        self.test_5_add_files()
        check_output('ml-git dataset commit dataset-ex')

    # Ml-git push example
    def test_7_push_files(self):

        # Create assert to ml-git push and messages
        self.test_6_commit_files()

        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r+") as c:
            config = yaml.safe_load(c)
            config["store"]["s3h"]["mlgit"]["endpoint-url"] = "http://127.0.0.1:9000"
            yaml.safe_dump(config, c)

        check_output('ml-git dataset push dataset-ex')
"""


if __name__ == "__main__":
   unittest.main()