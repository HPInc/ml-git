"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import git
import shutil
from integration_test.helper import check_output, clear, init_repository, BUCKET_NAME, PROFILE, add_file, \
    edit_config_yaml, create_spec, set_write_read, recursiva_write_read
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class CheckoutTagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_checkout_tag(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        clear(os.path.join(PATH_TEST, 'model'))
        clear(os.path.join(PATH_TEST, 'labels'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        check_output("ml-git dataset checkout computer-vision__images__dataset-ex__12")

        objects = os.path.join(ML_GIT_DIR, 'dataset', "objects")
        refs = os.path.join(ML_GIT_DIR, 'dataset', "refs")
        cache = os.path.join(ML_GIT_DIR, 'dataset', "cache")
        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "newfile0")

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

    def test_02_checkout_with_group_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=2:4 --seed=5"))

    def test_03_group_sample_with_amount_parameter_greater_than_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=4:2 --seed=5"))

    def test_04_group_sample_with_amount_parameter_equal_to_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=2:2 --seed=5"))

    def test_05_group_sample_with_group_size_parameter_greater_than_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[22], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=2:30 --seed=5"))

    def test_06_group_sample_with_group_size_parameter_less_than_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[41], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=2:-3 --seed=5"))

    def test_07_checkout_with_range_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=2:4:1"))

    def test_08_range_sample_with_start_parameter_greater_than_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=4:2:1"))

    def test_09_range_sample_with_start_parameter_less_than_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[42], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=-3:2:1"))

    def test_10_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[26], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=1:3:4"))

    def test_11_range_sample_with_start_parameter_equal_to_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=2:2:1"))

    def test_12_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[24], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --range-sample=2:30:1"))

    def test_13_checkout_with_random_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn('', check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --random-sample=2:3 --seed=3"))

    def test_14_random_sample_with_frequency_less_or_equal_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[40], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --random-sample=2:-2 --seed=3"))



    def test_15_random_sample_with_amount_parameter_greater_than_frequency(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[30], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --random-sample=4:2 --seed=3"))

    def test_16_random_sample_with_frequency_greater_or_equal_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[31], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --random-sample=2:10 --seed=3"))

    def test_17_random_sample_with_frequency_equal_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[29], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --random-sample=2:0 --seed=3"))

    def test_18_group_sample_with_group_size_parameter_equal_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[28], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=1:0 --seed=5"))

    def test_19_group_sample_with_amount_parameter_equal_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[43], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__12 --group-sample=0:1 --seed=5"))

    def test_20_model_related(self):
        clear(ML_GIT_DIR)
        tmpdir = os.path.join(PATH_TEST, "test_20_model_related")
        clear("test_20_model_related")
        os.makedirs("test_20_model_related")
        model = "model"
        dataset = "dataset"
        labels = "labels"
        os.chdir("test_20_model_related")
        git_server = os.path.join(tmpdir, "local_git_server.git")
        repo = git.Repo.init(git_server, bare=True)

        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[4] % git_server, check_output('ml-git ' + model + ' remote add "%s"' % git_server))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", model, "metadata")),
                      check_output('ml-git ' + model + ' init'))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_model = model + "\\" + model + "-ex"
        os.makedirs(workspace_model)
        version = 1
        create_spec(self, model, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_model, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[2] % git_server, check_output('ml-git ' + dataset + ' remote add "%s"' % git_server))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", dataset, "metadata")),
                      check_output('ml-git ' + dataset + ' init'))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_dataset = dataset + "\\" + dataset + "-ex"
        os.makedirs(workspace_dataset)
        version = 1
        create_spec(self, dataset, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_dataset, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[13], check_output('ml-git dataset add dataset-ex --bumpversion'))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))
        self.assertIn(messages[47], check_output('ml-git dataset push dataset-ex'))

        self.assertIn(messages[3] % git_server, check_output('ml-git ' + labels + ' remote add "%s"' % git_server))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", labels, "metadata")),
                      check_output('ml-git ' + labels + ' init'))
        edit_config_yaml(os.path.join(tmpdir, ".ml-git"))
        workspace_labels = labels + "\\" + labels + "-ex"
        os.makedirs(workspace_labels)
        version = 1
        create_spec(self, labels, tmpdir, version)
        with open(os.path.join(tmpdir, workspace_labels, 'file1'), "wb") as z:
            z.write(b'0' * 1024)

        self.assertIn(messages[15], check_output('ml-git labels add labels-ex --bumpversion'))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))
        self.assertIn(messages[47], check_output('ml-git labels push labels-ex'))

        self.assertIn(messages[14], check_output('ml-git model add model-ex --bumpversion'))
        self.assertIn(messages[17] % (os.path.join(tmpdir, ".ml-git", "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex --dataset=dataset-ex --labels=labels-ex"))
        self.assertIn(messages[47], check_output('ml-git model push model-ex'))
        set_write_read(os.path.join(tmpdir, workspace_model, 'file1'))
        set_write_read(os.path.join(tmpdir, workspace_dataset, 'file1'))
        set_write_read(os.path.join(tmpdir, workspace_labels, 'file1'))
        recursiva_write_read(os.path.join(tmpdir, ".ml-git"))
        shutil.rmtree(os.path.join(tmpdir, model))
        shutil.rmtree(os.path.join(tmpdir, dataset))
        shutil.rmtree(os.path.join(tmpdir, labels))
        shutil.rmtree(os.path.join(tmpdir, ".ml-git", model))
        shutil.rmtree(os.path.join(tmpdir, ".ml-git", dataset))
        shutil.rmtree(os.path.join(tmpdir, ".ml-git", labels))
        self.assertIn(messages[8] % (git_server, os.path.join(tmpdir, ".ml-git", model, "metadata")),
                      check_output('ml-git ' + model + ' init'))
        self.assertIn("", check_output(
            "ml-git model checkout computer-vision__images__model-ex__2 -d -l"))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, model)))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, dataset)))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, labels)))
        clear(tmpdir)
        clear("test_20_model_related")




