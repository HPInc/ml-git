"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import mock
import unittest
from mlgit.user_input import confirm
import io


class S3StoreTestCases(unittest.TestCase):

    def test_confirm_enforced(self):

        with mock.patch('builtins.input', return_value="Y"):
            self.assertTrue(confirm(''))

        with mock.patch('builtins.input', return_value="N"):
            self.assertFalse(confirm(''))

    def test_confirm_not_enforced(self):

        with mock.patch('builtins.input', return_value="Y"):
            self.assertTrue(confirm('', enforce_options=False))

        with mock.patch('builtins.input', return_value="N"):
            self.assertFalse(confirm('', enforce_options=False))

        with mock.patch('builtins.input', return_value="H"):
            self.assertFalse(confirm('', enforce_options=False))

        with mock.patch('sys.stdout', new=io.StringIO()) as fake_stdout, mock.patch('builtins.input', return_value="S"):
            self.assertFalse(confirm('', enforce_options=False))
            self.assertEqual('', fake_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
