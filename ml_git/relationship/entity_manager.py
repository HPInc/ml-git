"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.constants import SPEC_EXTENSION, FileType
from ml_git.relationship.github_manager import GithubManager
from ml_git.relationship.models.config import Config
from ml_git.relationship.models.entity import Entity
from ml_git.relationship.models.entity_version_relationships import EntityVersionRelationships
from ml_git.relationship.models.linked_entity import LinkedEntity
from ml_git.relationship.models.spec_version import SpecVersion
from ml_git.relationship.utils import export_relationships_to_csv, export_relationships_to_dot
from ml_git.utils import yaml_load_str


class EntityManager:
    """Class that operate over github api to manage entity's operations"""

    MLGIT_CONFIG_FILE = '/.ml-git/config.yaml'

    def __init__(self, github_token, url):
        self._manager = GithubManager(github_token, url)
        self._cache_entities = []

    def __is_config_repo(self, repository):
        """Returns True if the repository contains the file /.ml-git/config.yaml."""
        return self._manager.file_exists(repository, self.MLGIT_CONFIG_FILE)

    def __get_entities_from_config(self, stream):
        """Get entities found in config.yaml

        Args:
            stream (bytes): The stream of config.yaml file.

        Returns:
            list of objects of class Entity.
        """
        config_yaml = yaml_load_str(stream)
        config = Config(config_yaml)
        entities = []
        for remote in config.remotes.values():
            if not remote:
                continue

            repository = self._manager.find_repository(remote)
            for spec_path in self._manager.search_file(repository, SPEC_EXTENSION):
                spec_yaml = yaml_load_str(self._manager.get_file_content(repository, spec_path))
                entity = Entity(repository, spec_yaml)
                entities.append(entity)

        self._manager.alert_rate_limits()

        return entities

    def _get_entities_from_config(self, config_path):
        """Get entities found in config.yaml

        Args:
            config_path (str): The absolute path of config.yaml file.

        Returns:
            list of objects of class Entity.
        """
        self._cache_entities = []
        with open(config_path, 'rb') as config:
            self._cache_entities = self.__get_entities_from_config(config)
        return self._cache_entities

    def _get_entities_from_repo(self, repo_name):
        """Get entities found in config.yaml.

         Args:
             repo_name (str): The repository name where is the config.yaml is located in github.

         Returns:
             list of objects of class Entity.
         """
        self._cache_entities = []
        repo = self._manager.find_repository(repo_name)
        if repo is None or self.__is_config_repo(repo) is False:
            return

        config_bytes = self._manager.get_file_content(repo, self.MLGIT_CONFIG_FILE)
        self._cache_entities = self.__get_entities_from_config(config_bytes)

        return self._cache_entities

    def _get_entity_spec_path(self, repository, name):
        """Get the spec path of an entity

         Args:
             repository (github.Repository.Repository): Metadata repository object.
             name (str): The name of the entity you want to get the versions.

         Returns:
             Path of the entity
         """
        for spec_path in self._manager.search_file(repository, SPEC_EXTENSION):
            spec_file_name = '{}{}'.format(name, SPEC_EXTENSION)
            if (spec_path.lower()).endswith(spec_file_name.lower()):
                return spec_path
        raise Exception('It was not possible to find the entity.')

    def get_entities(self, config_path=None, config_repo_name=None):
        """Get a list of entities found in config.yaml.

        Args:
            config_path (str): The absolute path of the config.yaml file.
            config_repo_name (str): The repository name where is the config.yaml located in github.

        Returns:
            list of class Entity.
        """
        if config_repo_name:
            return self._get_entities_from_repo(config_repo_name)

        return self._get_entities_from_config(config_path)

    def _get_entity_versions(self, name, spec_path, repository):
        """Get a list of spec versions found for a specific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            spec_path (str): The path where the entity spec is located.
            repository (Repository): The instance of github.Repository.Repository.

        Returns:
            list of class SpecVersion.
        """

        versions = []

        for tag in repository.get_tags():
            if tag.name.split('__')[-2] != name:
                continue

            content = self._manager.get_file_content(repository, spec_path, tag.name)
            if not content:
                continue

            spec_tag_yaml = yaml_load_str(content)
            spec_version = SpecVersion(spec_tag_yaml)
            versions.append(spec_version)
        return versions

    def get_entity_versions(self, name, metadata_repo_name):
        """Get a list of spec versions found for a specific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            metadata_repo_name (str): The repository name where the entity metadata is located in GitHub.

        Returns:
            list of class SpecVersion.
        """
        repository = self._manager.find_repository(metadata_repo_name)
        spec_path = self._get_entity_spec_path(repository, name)
        self._manager.alert_rate_limits()

        return self._get_entity_versions(name, spec_path, repository)

    def _get_linked_entities(self, name, version, spec_path, repository):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            spec_path (str): The path where the entity spec is located.
            repository (Repository): The instance of github.Repository.Repository.

        Returns:
            list of LinkedEntity.
        """

        for tag in repository.get_tags():
            if tag.name.split('__')[-2] != name or tag.name.split('__')[-1] != str(version):
                continue

            content = self._manager.get_file_content(repository, spec_path, tag.name)
            if not content:
                continue

            spec_tag_yaml = yaml_load_str(content)
            entity = SpecVersion(spec_tag_yaml)

            return entity.get_related_entities_info()

    def get_linked_entities(self, name, version, metadata_repo_name):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            metadata_repo_name (str): The repository name where the metadata is located in GitHub.

        Returns:
            list of LinkedEntity.
        """
        repository = self._manager.find_repository(metadata_repo_name)
        spec_path = self._get_entity_spec_path(repository, name)

        self._manager.alert_rate_limits()
        return self._get_linked_entities(name, version, spec_path, repository)

    def get_entity_relationships(self, name, metadata_repo_name, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for an entity.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            metadata_repo_name (str): The repository name where the entity metadata is located in GitHub.
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
        repository = self._manager.find_repository(metadata_repo_name)
        spec_path = self._get_entity_spec_path(repository, name)
        entity_versions = self._get_entity_versions(name, spec_path, repository)

        relationships = {name: []}
        previous_version = None
        for entity_version in entity_versions:
            target_entity = LinkedEntity(entity_version.tag, entity_version.name,
                                         entity_version.version, entity_version.type)
            linked_entities = self._get_linked_entities(target_entity.name, target_entity.version,
                                                        spec_path, repository)
            if previous_version:
                linked_entities.append(LinkedEntity(previous_version.tag, previous_version.name, previous_version.version, previous_version.type))

            previous_version = target_entity
            relationships[name].append(EntityVersionRelationships(target_entity.version,
                                                                  target_entity.tag, linked_entities))

        if export_type == FileType.CSV.value:
            relationships = export_relationships_to_csv([entity_versions[0]], relationships, export_path)
        elif export_type == FileType.DOT.value:
            relationships = export_relationships_to_dot([entity_versions[0]], relationships, export_path)

        self._manager.alert_rate_limits()
        return relationships

    def get_project_entities_relationships(self, config_repo_name, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for all project entities.

        Args:
            config_repo_name (str): The repository name where the config is located in GitHub.
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
        project_entities = self.get_entities(config_repo_name=config_repo_name)

        config_repo = self._manager.find_repository(config_repo_name)
        if config_repo is None or self.__is_config_repo(config_repo) is False:
            return
        config_bytes = self._manager.get_file_content(config_repo, self.MLGIT_CONFIG_FILE)
        config_yaml = yaml_load_str(config_bytes)
        config = Config(config_yaml)

        all_relationships = {}
        for entity in project_entities:
            entity_relationships = self.get_entity_relationships(entity.name, config.get_entity_type_remote(entity.type))
            all_relationships[entity.name] = entity_relationships[entity.name]

        if export_type == FileType.CSV.value:
            all_relationships = export_relationships_to_csv(project_entities, all_relationships, export_path)
        elif export_type == FileType.DOT.value:
            all_relationships = export_relationships_to_dot(project_entities, all_relationships, export_path)

        self._manager.alert_rate_limits()
        return all_relationships
