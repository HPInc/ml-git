"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.repository import Repository
from mlgit.config import config_load


DATASET = "dataset"
LABELS = "labels"
MODEL = "model"
PROJECT = "project"


def init_repository(entity_type="dataset"):
    return Repository(config_load(), entity_type)


repositories = {
    DATASET: init_repository(DATASET),
    LABELS: init_repository(LABELS),
    MODEL: init_repository(MODEL),
    PROJECT: init_repository(PROJECT)
}
