"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
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

    def test_01_init_root_directory(self):
        self.assertIn(messages[0],check_output("ml-git init"))
        config = os.path.join(ML_GIT_DIR, "config.yaml")
        self.assertTrue(os.path.exists(config))

    def test_02_init_subfoldery(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        os.chdir(".ml-git")
        self.assertIn(messages[1],check_output("ml-git init"))

    def test_03_init_already_initialized_repository(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[1],check_output("ml-git init"))

    def test_04_add_remote_dataset(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["dataset"]["git"])

    def test_05_add_remote_labels(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[3] % GIT_PATH,check_output('ml-git labels remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["labels"]["git"])

    def test_06_add_remote_model(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[4] % GIT_PATH,check_output('ml-git model remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR,"config.yaml"),"r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["model"]["git"])

    def test_07_add_remote_subfolder(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))

        # assertion: 5 - Add remote to an uninitialized directory
    def test_08_add_remote_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[6],check_output('ml-git dataset remote add "%s"' % GIT_PATH))

    def test_09_change_remote_rempository(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[5] % (GIT_PATH, GIT_PATH),check_output('ml-git dataset remote add "%s"' % GIT_PATH))

    def test_10_add_store_root_directory(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output("ml-git init"))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])

    def test_11_add_store_again(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE), check_output(
            "ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output(
            "ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

    def test_12_add_store_subfolder(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

    def test_13_add_store_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[6],check_output("ml-git store add %s --credentials=%s --region=us-east-1" % (BUCKET_NAME, PROFILE)))

    def test_14_init_dataset(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn( messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

    def test_15_initialize_dataset_twice_entity(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset init"))
        self.assertIn(messages[9] % os.path.join(ML_GIT_DIR, "dataset", "metadata"),check_output("ml-git dataset init"))

    def test_16_initialize_dataset_from_subfolder(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

    def test_17_initialize_dataset_from_wrong_repository(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_WRONG_REP,check_output('ml-git dataset remote add %s' % GIT_WRONG_REP))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[10] % GIT_WRONG_REP, check_output("ml-git dataset init"))

        # assertion:5 - Try to init without configuring remote and storage
    def test_18_initialize_dataset_without_repository_and_storange(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[11],check_output("ml-git dataset init"))

        # assertion: 6 - Run the command  to LABELS
    def test_19_initialize_labels(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[3] % GIT_PATH,check_output('ml-git labels remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "labels", "metadata")),check_output("ml-git labels init"))

    def test_19_initialize_model(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[4] % GIT_PATH,check_output('ml-git model remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "model", "metadata")),check_output("ml-git model init"))

    def test_20_add_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '', self)

    def test_21_add_files_to_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        add_file('model', '', self)

    def test_22_add_files_to_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        add_file('labels', '', self)

        # Assertion 6 - Run the command with parameter (--bumpversion)
    def test_23_add_files_with_bumpversion(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '--bumpversion', self)

    def test_24_commit_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
             os.path.join('computer-vision', 'images', 'dataset-ex')),
             check_output("ml-git dataset commit dataset-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_25_commit_files_to_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        add_file('labels', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_26_commit_files_to_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        add_file('model', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_27_push_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))
        edit_config_yaml()

        check_output('ml-git dataset push dataset-ex')

    def test_28_push_files_to_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        add_file('labels', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))
        edit_config_yaml()
        check_output('ml-git labels push labels-ex')

    def test_29_push_files_to_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        add_file('model', '', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))
        edit_config_yaml()
        check_output('ml-git model push model-ex')

    def test_30_get_tag(self):
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
        file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "file0")

        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))
        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(index))
        self.assertTrue(os.path.exists(cache))

    def test_31_get_with_group_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output("ml-git dataset get computer-vision__images__dataset-ex__5 --group-sample=2:4 --seed=5"))

    def test_32_get_with_range_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --range-sample=2:4:1"))

    def test_33_range_sample_with_start_parameter_greater_than_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --range-sample=4:2:1"))

    def test_34_range_sample_with_start_parameter_equal_to_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --range-sample=4:2:1"))

    def test_35_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[24], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --range-sample=2:30:1"))

    def test_36_group_sample_with_amount_parameter_greater_than_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --group-sample=4:2 --seed=5"))

    def test_37_group_sample_with_amount_parameter_equal_to_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --group-sample=2:2 --seed=5"))

    def test_38_group_sample_with_group_size_parameter_greater_than_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[22], check_output(
            "ml-git dataset get computer-vision__images__dataset-ex__5 --group-sample=2:30 --seed=5"))

    def test_39_status_after_put_on_new_file_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        workspace = "dataset/dataset-ex"
        clear(workspace)

        os.makedirs(workspace)

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 5
            }
        }

        with open(os.path.join(workspace, "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

            with open(os.path.join(workspace, 'file'), "wb") as z:
                z.write(b'0' * 1024)
        self.assertRegex(check_output("ml-git dataset status dataset-ex"), r"Changes to be committed\s+untracked files\s+dataset-ex\.spec")


if __name__ == "__main__":
   unittest.main()