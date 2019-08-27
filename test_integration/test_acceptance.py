"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from test_integration.helper import execute, clear

from test_integration.output_messages import messages


PATH_TEST = os.path.join(os.getcwd(), ".test_env")

ML_GIT_DIR = os.path.join(os.getcwd(), PATH_TEST, ".ml-git")

GIT_PATH = os.path.join(PATH_TEST, "local_git_server.git")

BUCKET_NAME = "mlgit"

PROFILE = "default"

SUCCESS = 0


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)

    # Check the result of  "init" command
    def test_1_init(self):

        # assertion: 1 - Run the command in the project root directory
        output = execute("ml-git init")

        self.assertEqual(output, messages[0] % ML_GIT_DIR)

        config = os.path.join(ML_GIT_DIR, "config.yaml")

        self.assertTrue(os.path.exists(config))

        # assertion: 2 -
        os.chdir(".ml-git")

        output = execute("ml-git init")

        self.assertEqual(output, messages[1] % ML_GIT_DIR)

        # assertion: 3 - Attempt to initialize an already initialized repository
        os.chdir(ML_GIT_DIR)

        output = execute("ml-git init")
        
        self.assertEqual(output, messages[1] % ML_GIT_DIR)

        clear(ML_GIT_DIR)

    # Add a remote to dataset/labels/model entity
    def test_2_add_remote(self):

        execute("ml-git init")

        # assertion: 1 - Run the command  to DATASET
        output = execute("ml-git dataset remote add %s" % GIT_PATH)

        self.assertEqual(output, messages[2] % GIT_PATH)

        # assertion: 2 - Run the command  to LABELS
        output = execute("ml-git labels remote add %s" % GIT_PATH)

        self.assertEqual(output, messages[3] % GIT_PATH)

        # assertion: 3 - Run the command  to MODEL
        output = execute("ml-git model remote add %s" % GIT_PATH)

        self.assertEqual(output, messages[4] % GIT_PATH)

        os.chdir(ML_GIT_DIR)

        # assertion: 4 - Type the command from a different place of the project root
        output = execute("ml-git dataset remote add %s" % GIT_PATH)

        self.assertEqual(output, messages[5] % (GIT_PATH, GIT_PATH))

        os.chdir(PATH_TEST)

        clear(ML_GIT_DIR)

        # assertion: 5 - Add remote to an uninitialized directory
        output = execute("ml-git dataset remote add %s" % GIT_PATH)

        self.assertEqual(output, messages[6])

    def test_3_add_store(self):

        execute("ml-git init")

        output = execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))

        # assertion: 1 - Run the command in the project root directory
        self.assertEqual(output, messages[7] % (BUCKET_NAME, PROFILE))

        output = execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))

        # assertion: 2 - Add the same store again
        self.assertEqual(output, messages[7] % (BUCKET_NAME, PROFILE))

        os.chdir(ML_GIT_DIR)

        output = execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))

        # assertion: 3 - Type the command from a different place of the project root
        self.assertEqual(output, messages[7] % (BUCKET_NAME, PROFILE))

        clear(ML_GIT_DIR)

    def test_4_init_dataset(self):
        # assertion: 1 - Run the command  to DATASET
        execute("ml-git init")
        execute("ml-git dataset remote add %s" % GIT_PATH)
        execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))
        output = execute("ml-git dataset init")

        self.assertEqual(output, messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR,"dataset","metadata")))

        # assertion: 2 - Initialize twice the entity
        output = execute("ml-git dataset init")

        self.assertEqual(output, messages[9] % os.path.join(ML_GIT_DIR,"dataset","metadata"))

        clear(ML_GIT_DIR)

        # assertion: 3 - Type the command from a different place of the project root
        execute("ml-git init")
        execute("ml-git dataset remote add %s" % GIT_PATH)
        execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))

        os.chdir(ML_GIT_DIR)

        output = execute("ml-git dataset init")

        self.assertEqual(output, messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR,"dataset","metadata")))

        # assertion:5 - Try to init without configuring remote and storage
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        execute("ml-git init")
        output = execute("ml-git dataset init")
        self.assertEqual(output, messages[11])

        # assertion: 6 - Run the command  to LABELS
        output = execute("ml-git labels remote add %s" % GIT_PATH)
        self.assertEqual(output, messages[3] % GIT_PATH)

        output = execute("ml-git labels init")

        self.assertEqual(output, messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR,"labels","metadata")))

        # assertion: 7 - Run the command  to MODEL
        output = execute("ml-git model remote add %s" % GIT_PATH)
        self.assertEqual(output, messages[12] % GIT_PATH)
        output = execute("ml-git model init")
        self.assertEqual(output, messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "model", "metadata")))

    def test_5_add_files(self):

        execute("ml-git init")
        execute("ml-git dataset remote add %s" % os.path.join(PATH_TEST, "invalid_repo.git"))
        execute("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE))



if __name__ == "__main__":
   unittest.main()