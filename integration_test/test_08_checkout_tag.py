"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import sys
import unittest
import git
import shutil
from integration_test.helper import check_output, clear, init_repository, BUCKET_NAME, PROFILE, add_file, \
    edit_config_yaml, create_spec, set_write_read, recursive_write_read, entity_init
from integration_test.helper import PATH_TEST, ML_GIT_DIR, STORE_TYPE

from integration_test.commands import *
from integration_test.output_messages import messages


class CheckoutTagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_checkout(self, entity):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))
        init_repository("dataset", self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, entity, "metadata")),
                      check_output(MLGIT_UPDATE % entity))

    def test_01_checkout_tag(self):
        self.set_up_checkout("dataset")

        check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12"))

        objects = os.path.join(ML_GIT_DIR, "dataset", "objects")
        refs = os.path.join(ML_GIT_DIR, "dataset", "refs")
        cache = os.path.join(ML_GIT_DIR, "dataset", "cache")
        spec_file = os.path.join(PATH_TEST, "dataset", "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        file = os.path.join(PATH_TEST, "dataset", "computer-vision", "images", "dataset-ex", "newfile0")

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

    def test_02_checkout_with_group_sample(self):
        self.set_up_checkout("dataset")
        check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12 --sample-type=group "
                                                  "--sampling=2:4 --seed=5"))

    def test_03_group_sample_with_amount_parameter_greater_than_group_size(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[21], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=4:2 --seed=5"))

    def test_04_group_sample_with_amount_parameter_equal_to_group_size(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[21], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=2:2 --seed=5"))

    def test_05_group_sample_with_group_size_parameter_greater_than_list_size(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[22], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=2:30 --seed=5"))

    def test_06_group_sample_with_group_size_parameter_less_than_zero(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[41], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=-2:3 --seed=5"))

    def test_07_checkout_with_range_sample(self):
        self.set_up_checkout("dataset")
        self.assertIn("", check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                       + " --sample-type=range --sampling=2:4:1"))

    def test_08_range_sample_with_start_parameter_greater_than_stop(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=range --sampling=4:2:1"))

    def test_09_range_sample_with_start_parameter_less_than_zero(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=range --sampling=3:2:1"))

    def test_10_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[26], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=range --sampling=1:3:4"))

    def test_11_range_sample_with_start_parameter_equal_to_stop(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[23], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=range --sampling=2:2:1"))

    def test_12_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[24], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=range --sampling=2:30:1"))

    def test_13_checkout_with_random_sample(self):
        self.set_up_checkout("dataset")

        self.assertIn('', check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                       + " --sample-type=random --sampling=2:3 --seed=3"))

    def test_14_random_sample_with_frequency_less_or_equal_zero(self):
        self.set_up_checkout("dataset")

        self.assertIn(messages[30], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=random --sampling=2:2 --seed=3"))

    def test_15_random_sample_with_amount_parameter_greater_than_frequency(self):
        self.set_up_checkout("dataset")

        self.assertIn(messages[30], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=random --sampling=4:2 --seed=3"))

    def test_16_random_sample_with_frequency_greater_or_equal_list_size(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[31], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=random --sampling=2:10 --seed=3"))

    def test_17_random_sample_with_frequency_equal_zero(self):
        self.set_up_checkout("dataset")

        self.assertIn(messages[29], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=random --sampling=2:0 --seed=3"))

    def test_18_group_sample_with_group_size_parameter_equal_zero(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[28], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=1:0 --seed=5"))

    def test_19_group_sample_with_amount_parameter_equal_zero(self):
        self.set_up_checkout("dataset")
        self.assertIn(messages[43], check_output(MLGIT_CHECKOUT % ("dataset", "computer-vision__images__dataset-ex__12")
                                                 + " --sample-type=group --sampling=0:1 --seed=5"))

    def test_20_model_related(self):
        clear(ML_GIT_DIR)
        tmpdir = os.path.join(PATH_TEST, "test_20_model_related")
        clear(tmpdir)
        os.makedirs(tmpdir)
        model = "model"
        dataset = "dataset"
        labels = "labels"
        os.chdir(tmpdir)
        git_server = os.path.join(tmpdir, "local_git_server.git")
        repo = git.Repo.init(git_server, bare=True)

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (git_server, model), check_output(MLGIT_REMOTE_ADD % (model, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", model, "metadata")),
                      check_output(MLGIT_ENTITY_INIT % "model"))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_model = os.path.join(model, model + "-ex")
        os.makedirs(workspace_model)
        version = 1
        create_spec(self, model, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_model, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[2] % (git_server, dataset), check_output(MLGIT_REMOTE_ADD % (dataset, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", dataset, "metadata")),
                      check_output(MLGIT_ENTITY_INIT % "dataset"))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_dataset = os.path.join(dataset, dataset + "-ex")
        os.makedirs(workspace_dataset)
        version = 1
        create_spec(self, dataset, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_dataset, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ("dataset", "dataset-ex")))

        self.assertIn(messages[2] % (git_server, labels), check_output(MLGIT_REMOTE_ADD % (labels, git_server)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", labels, "metadata")),
                      check_output(MLGIT_ENTITY_INIT % labels))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_labels = os.path.join(labels, labels + "-ex")
        os.makedirs(workspace_labels)
        version = 1
        create_spec(self, labels, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_labels, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[15], check_output(MLGIT_ADD % ("labels", "labels-ex", "--bumpversion")))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output(MLGIT_COMMIT % ("labels", "labels-ex", "")))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ("labels", "labels-ex")))

        self.assertIn(messages[14], check_output(MLGIT_ADD % ("model", "model-ex", "--bumpversion")))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output(MLGIT_COMMIT % ("model", "model-ex", "--dataset=dataset-ex") + " --labels=labels-ex"))
        self.assertIn(messages[47], check_output(MLGIT_PUSH % ("model", "model-ex")))
        set_write_read(os.path.join(tmpdir, workspace_model, 'file1'))
        set_write_read(os.path.join(tmpdir, workspace_dataset, 'file1'))
        set_write_read(os.path.join(tmpdir, workspace_labels, 'file1'))
        if not sys.platform.startswith('linux'):
            recursive_write_read(os.path.join(tmpdir, ".ml-git"))
        clear(os.path.join(tmpdir, model))
        clear(os.path.join(tmpdir, dataset))
        clear(os.path.join(tmpdir, labels))
        clear(os.path.join(tmpdir, ".ml-git", model))
        clear(os.path.join(tmpdir, ".ml-git", dataset))
        clear(os.path.join(tmpdir, ".ml-git", labels))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", model, "metadata")),
                      check_output(MLGIT_ENTITY_INIT % model))
        self.assertIn("", check_output(MLGIT_CHECKOUT % ("model", "computer-vision__images__model-ex__2")
                                       + " -d -l"))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, model)))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, dataset)))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, labels)))
        os.chdir(PATH_TEST)
        clear(tmpdir)
