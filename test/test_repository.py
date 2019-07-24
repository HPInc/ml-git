"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
from mlgit.repository import Repository
from mlgit.config import *
from mlgit.sample import Sample


class LocalRepositoryTestCases(unittest.TestCase):

    def test_sample_validation(self):
        samples = {'sample':'1:2', 'seed':'2'}
        samples_ = {'sample':'10:1', 'seed':'3'}
        samples__ = {'sample': 'r:f', 'seed': 'f'}

        config = config_load()
        r = Repository(config)

        sample_aux = Sample(1, 2, 2)
        sample_aux2 = Sample(1, 2, 5)
        sample = r.sample_validition(samples)
        self.assertEqual(type(sample), type(sample_aux))
        self.assertNotEqual(sample, sample_aux2)
        self.assertIsNone(r.sample_validition(samples_))
        self.assertIsNone(r.sample_validition(samples__))























    if __name__ == "__main__":
        unittest.main()