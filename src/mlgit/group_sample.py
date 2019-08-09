"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class GroupSample:

    def __init__(self, amount, group_size, seed):
        self.amount = amount
        self.group_size = group_size
        self.seed = seed

    def get_amount(self):
        return self.amount

    def get_group_size(self):
        return self.group_size
        
    def get_seed(self):
        return self.seed