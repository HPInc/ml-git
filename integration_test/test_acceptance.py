"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, init_repository, add_file, edit_config_yaml
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
        init_repository('dataset', self)
        add_file('dataset', '', self)

        # Assertion 2: - Run the command  to MODEL
        init_repository('model', self)
        add_file('model', '', self)

        # Assertion 3: - Run the command  to LABELS
        init_repository('labels', self)
        add_file('labels', '', self)

        # Assertion 6 - Run the command with parameter (--bumpversion)
        add_file('dataset', '--bumpversion', self)

        '''
        # Assertion: 8 - Run command with a deleted file
        remove_file('dataset')
        self.assertIn(messages[13], check_output('ml-git dataset add dataset-ex --del'))
        '''

    def test_6_commit_files(self):

        # # Assertion 1 - Run the command  to DATASET
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
             os.path.join('computer-vision', 'images', 'dataset-ex')),
             check_output("ml-git dataset commit dataset-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

        # Assertion 2 - Run the command  to LABELS
        init_repository('labels', self)
        add_file('labels', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

        # Assertion 3 - Run the command  to MODEL
        init_repository('model', self)
        add_file('model', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_7_push_files(self):

        # Assertion 1 - Run the command  to DATASET
        clear(ML_GIT_DIR)
        self.test_6_commit_files()

        edit_config_yaml()

        check_output('ml-git dataset push dataset-ex')

        # Assertion 2 - Run the command  to LABELS
        check_output('ml-git labels push labels-ex')

        # Assertion 3 - Run the command  to MODEL
        check_output('ml-git model push model-ex')

        # Assertion 4 - Twice push
        self.assertIn(messages[18], check_output('ml-git dataset push dataset-ex'))

    def test_8_get_tag(self):

        # Assertion 1 - Get the dataset with success
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        clear(os.path.join(PATH_TEST, 'model'))
        clear(os.path.join(PATH_TEST, 'labels'))
        init_repository('dataset', self)

        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output("ml-git dataset get computer-vision__images__dataset-ex__5"))

        cache = os.path.join(ML_GIT_DIR, 'dataset', "cache")
        index = os.path.join(ML_GIT_DIR, 'dataset', "index")
        objects = os.path.join(ML_GIT_DIR, 'dataset', "objects")
        refs = os.path.join(ML_GIT_DIR, 'dataset', "refs")
        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "file")

        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(index))
        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(spec_file))
        self.assertTrue(os.path.exists(file))

if __name__ == "__main__":
   unittest.main()