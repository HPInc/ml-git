"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

"""ML-Git API

Use the ML-Git API to make a checkout of an ML-Entity.

Example of how import the ml-git api:
    from mlgit import api

Attributes:
    config: The config file of an ml-git project.
"""
import os

from mlgit import log
from mlgit.config import config_load
from mlgit.repository import Repository
from mlgit.log import init_logger

init_logger()


def validate_sample(sampling):
    if 'group' in sampling or 'random' in sampling:
        if 'seed' not in sampling:
            log.error("It is necessary to pass the attribute 'seed' in 'sampling'. Example: {'group': '1:2', "
                      "'seed': '10'}.")
            return False
    elif 'range' not in sampling:
        log.error('To use the sampling option, you must pass a valid type of sampling (group, '
                  'random or range).')
        return False
    return True


def checkout(entity, tag, sampling=None, retries=2, force=False, dataset=False, labels=False):
    """This command allows retrieving the data of a specific version of an ML entity.

    Example:
        checkout('dataset', 'computer-vision__images3__imagenet__1')

    Args:
        entity (str): The type of an ML entity. (dataset, labels or model)
        tag (str): An ml-git tag to identify a specific version of an ML entity.
        sampling (dict): group: <amount>:<group> The group sample option consists of amount and group used to
                                 download a sample.\n
                         range: <start:stop:step> The range sample option consists of start, stop and step used
                                to download a sample. The start parameter can be equal or greater than zero. The
                                stop parameter can be 'all', -1 or any integer above zero.\n
                         random: <amount:frequency> The random sample option consists of amount and frequency
                                used to download a sample.
                         seed: The seed is used to initialize the pseudorandom numbers.
        retries (int, optional): Number of retries to download the files from the storage [default: 2].
        force (bool, optional): Force checkout command to delete untracked/uncommitted files from the local repository.
        dataset (bool, optional): If exist a dataset related with the model or labels, this one must be downloaded.
        labels (bool, optional): If exist labels related with the model, they must be downloaded.

    Returns:
        str: Return the path where the data was checked out.

    """

    r = Repository(config_load(), entity)
    r.update()
    if sampling is not None and not validate_sample(sampling):
        return None
    r.checkout(tag, sampling, retries, force, dataset, labels)

    data_path = os.path.join(entity, *tag.split("__")[:-1])
    if not os.path.exists(data_path):
        data_path = None
    return data_path
