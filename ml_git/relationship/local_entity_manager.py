"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
from collections import namedtuple

from git import Repo

from ml_git import log
from ml_git._metadata import MetadataManager
from ml_git.config import config_load
from ml_git.constants import SPEC_EXTENSION, FileType, EntityType
from ml_git.ml_git_message import output_messages
from ml_git.relationship.models.entity import Entity
from ml_git.relationship.models.entity_version_relationships import EntityVersionRelationships
from ml_git.relationship.models.linked_entity import LinkedEntity
from ml_git.relationship.models.spec_version import SpecVersion
from ml_git.relationship.utils import export_relationships_to_csv, export_relationships_to_dot
from ml_git.utils import yaml_load_str, get_root_path


class LocalEntityManager:
    """Class that operate over local git repository to manage entity's operations"""

    def __init__(self):
        self._manager = None

    def __init_manager(self, type_entity):
        try:
            get_root_path()
            config = config_load()
            if not config[type_entity]['git']:
                log.warn(output_messages['ERROR_REPOSITORY_NOT_FOUND'])
                return
            self._manager = MetadataManager(config, repo_type=type_entity)
            if not self._manager.check_exists():
                self._manager.init()
        except Exception as e:
            log.error(e)

    def get_entities(self):
        """Get a list of entities found in config.yaml.

        Returns:
            list of class Entity.
        """
        entities = []
        metadata_repository = namedtuple('Repository', ['private', 'full_name', 'ssh_url', 'html_url', 'owner'])
        metadata_owner = namedtuple('Owner', ['email', 'name'])
        for type_entity in EntityType:
            self.__init_manager(type_entity.value)
            if not self._manager:
                continue
            repository = metadata_repository(False, '', '', '', metadata_owner('', ''))
            for obj in Repo(self._manager.path).head.commit.tree.traverse():
                if SPEC_EXTENSION in obj.name:
                    entity_spec = yaml_load_str(io.BytesIO(obj.data_stream.read()))
                    entity = Entity(repository, entity_spec)
                    if entity.type in type_entity.value and entity not in entities:
                        entities.append(entity)

        return entities

    def __get_spec_each_tag(self, name, version=None):
        for tag in self._manager.list_tags(name, True):
            if version and tag.name.split('__')[-1] != str(version):
                continue
            content = None
            for obj in tag.commit.tree.traverse():
                if obj.name == name + SPEC_EXTENSION:
                    content = io.BytesIO(obj.data_stream.read())
                    break
            if not content:
                continue
            yield content

    def get_entity_versions(self, name, type_entity):
        """Get a list of spec versions found for an specific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            type_entity (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of class SpecVersion.
        """

        self.__init_manager(type_entity)

        if not self._manager:
            return

        versions = []
        for content in self.__get_spec_each_tag(name):
            spec_tag_yaml = yaml_load_str(content)
            spec_version = SpecVersion(spec_tag_yaml)
            versions.append(spec_version)
        return versions

    def get_linked_entities(self, name, version, type_entity):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            type_entity (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of LinkedEntity.
        """

        self.__init_manager(type_entity)

        if not self._manager:
            return

        for content in self.__get_spec_each_tag(name, version):
            spec_tag_yaml = yaml_load_str(content)
            entity = SpecVersion(spec_tag_yaml)
            return entity.get_related_entities_info()

    def get_entity_relationships(self, name, type_entity, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for an entity.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            type_entity (str): The type of the ml-entity (datasets, models, labels).
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """

        entity_versions = self.get_entity_versions(name, type_entity)
        if not entity_versions:
            return

        relationships = {name: []}
        previous_version = None
        for entity_version in entity_versions:
            target_entity = LinkedEntity(entity_version.tag, entity_version.name,
                                         entity_version.version, entity_version.type)
            linked_entities = self.get_linked_entities(target_entity.name, target_entity.version, type_entity)

            if previous_version:
                linked_entities.append(LinkedEntity(previous_version.tag, previous_version.name, previous_version.version, previous_version.type))

            previous_version = target_entity
            relationships[name].append(EntityVersionRelationships(target_entity.version,
                                                                  target_entity.tag, linked_entities))

        if export_type == FileType.CSV.value:
            relationships = export_relationships_to_csv([entity_versions[0]], relationships, export_path)
        elif export_type == FileType.DOT.value:
            relationships = export_relationships_to_dot([entity_versions[0]], relationships, export_path)
        return relationships

    def get_project_entities_relationships(self, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for all project entities.

        Args:
            export_type (str): Set the format of the return [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
        project_entities = self.get_entities()
        if not project_entities:
            return []

        all_relationships = {}
        for entity in project_entities:
            type_entity = entity.type if entity.type.endswith('s') else '{}s'.format(entity.type)
            entity_relationships = self.get_entity_relationships(entity.name, type_entity)
            all_relationships[entity.name] = entity_relationships[entity.name]

        if export_type == FileType.CSV.value:
            all_relationships = export_relationships_to_csv(project_entities, all_relationships, export_path)
        elif export_type == FileType.DOT.value:
            all_relationships = export_relationships_to_dot(project_entities, all_relationships, export_path)

        return all_relationships
