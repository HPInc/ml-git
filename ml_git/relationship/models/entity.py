"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json

from ml_git.relationship.models.spec_version import SpecVersion
from ml_git.relationship.models.metadata import Metadata


class Entity:
    """Class that represents an ml-entity.

    Attributes:
        name (str): The name of the entity.
        entity_type (str): The type of the ml-entity (datasets, models, labels).
        private (str): The access of entity metadata.
        metadata (Metadata): The metadata of the entity.
        last_spec_version (SpecVersion): The specification file of the entity last version.
    """

    def __init__(self, repository, spec_yaml):
        self.last_spec_version = SpecVersion(spec_yaml)
        self.name = self.last_spec_version.name
        self.type = self.last_spec_version.type
        self.metadata = Metadata(repository)
        self.private = repository.private

    def to_dict(self, obj):
        attrs = obj.__dict__.copy()
        ignore_attributes = ['last_spec_version', 'metadata']
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr] or attr in ignore_attributes:
                del attrs[attr]
        attrs['metadata'] = Metadata.to_dict(self.metadata)
        attrs['last_spec_version'] = self.last_spec_version.to_dict(self.last_spec_version)
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Entity):
            return self.name == other.name and self.type == other.type
        return False
