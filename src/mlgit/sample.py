"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class Sample:

    def __init__(self, amount, group, seed):
        self.amount = amount
        self.group = group
        self.seed = seed

    def get_amount(self):
        return self.amount

    def get_group(self):
        return self.group

    def get_seed(self):
        return self.seed
