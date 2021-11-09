"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import shutil
import humanize

from git import Repo, GitError
from halo import Halo

from ml_git import log
from ml_git._metadata import MetadataManager
from ml_git.config import get_refs_path, get_sample_spec_doc
from ml_git.constants import METADATA_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME, ROOT_FILE_NAME, MutabilityType, \
    SPEC_EXTENSION, MANIFEST_FILE, EntityType, STORAGE_SPEC_KEY, DATASET_SPEC_KEY, LABELS_SPEC_KEY, \
    MLGIT_IGNORE_FILE_NAME
from ml_git.manifest import Manifest
from ml_git.ml_git_message import output_messages
from ml_git.plugin_interface.data_plugin_constants import ADD_METADATA
from ml_git.plugin_interface.plugin_especialization import PluginCaller
from ml_git.refs import Refs
from ml_git.spec import spec_parse, get_entity_dir, get_spec_key
from ml_git.utils import ensure_path_exists, yaml_save, yaml_load, clear, get_file_size, normalize_path


class Metadata(MetadataManager):
    def __init__(self, spec, metadata_path, config, repo_type=EntityType.DATASETS.value):
        self.__repo_type = repo_type
        self._spec = spec
        self.__path = metadata_path
        self.__config = config
        super(Metadata, self).__init__(config, repo_type)

    def tag_exists(self, index_path):
        spec_file = os.path.join(index_path, 'metadata', self._spec, self._spec + SPEC_EXTENSION)
        full_metadata_path, entity_sub_path, metadata = self._full_metadata_path(spec_file)
        if metadata is None:
            return full_metadata_path, entity_sub_path, metadata

        # generates a tag to associate to the commit
        tag = self.metadata_tag(metadata)

        # check if tag already exists in the ml-git repository
        tags = self._tag_exists(tag)
        if len(tags) > 0:
            log.error(output_messages['ERROR_TAG_ALREADY_EXISTS_CONSIDER_USER_VERSION'] % (tag, self.__repo_type), class_name=METADATA_CLASS_NAME)
            return None, None, None
        return full_metadata_path, entity_sub_path, metadata

    def commit_metadata(self, index_path, tags, commit_msg, changed_files, mutability, ws_path):
        spec_file = os.path.join(index_path, 'metadata', self._spec, self._spec + SPEC_EXTENSION)
        full_metadata_path, entity_sub_path, metadata = self._full_metadata_path(spec_file)
        log.debug(output_messages['DEBUG_METADATA_PATH'] % full_metadata_path, class_name=METADATA_CLASS_NAME)

        if full_metadata_path is None:
            return None, None
        elif entity_sub_path is None:
            return None, None

        ensure_path_exists(full_metadata_path)

        ret = self.__commit_manifest(full_metadata_path, index_path, changed_files, mutability)
        if ret is False:
            log.info(output_messages['INFO_NO_FILES_COMMIT_FOR'] % self._spec, class_name=METADATA_CLASS_NAME)
            return None, None

        try:
            self.__commit_metadata(full_metadata_path, index_path, metadata, tags, ws_path)
        except Exception:
            return None, None
        # generates a tag to associate to the commit
        tag = self.metadata_tag(metadata)

        # check if tag already exists in the ml-git repository
        tags = self._tag_exists(tag)
        if len(tags) > 0:
            log.error(output_messages['ERROR_TAG_ALREADY_EXISTS_CONSIDER_USER_VERSION'] % tag, class_name=METADATA_CLASS_NAME)
            for t in tags:
                log.error(output_messages['ERROR_METADATA_MESSAGE'] % t)
            return None, None

        if commit_msg is not None and len(commit_msg) > 0:
            msg = commit_msg
        else:
            # generates a commit message
            msg = self.metadata_message(metadata)
        log.debug(output_messages['DEBUG_COMMIT_MESSAGE'] % msg, class_name=METADATA_CLASS_NAME)
        sha = self.commit(entity_sub_path, msg)
        self.tag_add(tag)
        return str(tag), str(sha)

    def metadata_subpath(self, metadata):
        sep = os.sep
        path = self.__metadata_spec(metadata, sep)
        log.debug(output_messages['DEBUG_DATASET_PATH'] % path, class_name=METADATA_CLASS_NAME)
        return path

    def _full_metadata_path(self, spec_file):
        try:
            entity_dir = get_entity_dir(self.__repo_type, self._spec)
        except Exception as e:
            log.error(e, class_name=METADATA_CLASS_NAME)
            return None, None, None
        metadata = yaml_load(spec_file)
        full_metadata_path = os.path.join(self.__path, entity_dir)
        return full_metadata_path, entity_dir, metadata

    @Halo(text='Commit manifest', spinner='dots')
    def __commit_manifest(self, full_metadata_path, index_path, changed_files, mutability):
        # Append index/files/MANIFEST.yaml to .ml-git/dataset/metadata/ <categories>/MANIFEST.yaml
        idx_path = os.path.join(index_path, 'metadata', self._spec, MANIFEST_FILE)
        if os.path.exists(idx_path) is False:
            log.error(output_messages['ERROR_NO_MANIFEST_FILE_FOUND'] % idx_path, class_name=METADATA_CLASS_NAME)
            return False
        full_path = os.path.join(full_metadata_path, MANIFEST_FILE)
        mobj = Manifest(full_path)
        if mutability == MutabilityType.MUTABLE.value or mutability == MutabilityType.FLEXIBLE.value:
            for key, file in changed_files:
                mobj.rm(key, file)
        mobj.merge(idx_path)
        mobj.save()
        del (mobj)
        os.unlink(idx_path)
        return True

    def get_metadata_path(self, tag):
        _, specname, _ = spec_parse(tag)
        entity_dir = get_entity_dir(self.__repo_type, specname)
        return os.path.join(self.__path, entity_dir)

    def _copy_to_metadata_path(self, src_path, full_metadata_path, file_name):
        if os.path.exists(src_path):
            dst_path = os.path.join(full_metadata_path, file_name)
            try:
                shutil.copy2(src_path, dst_path)
            except Exception as e:
                log.error(output_messages['ERROR_COULD_NOT_FIND_FILE'] % file_name,
                          class_name=METADATA_CLASS_NAME)
                raise e

    def __commit_metadata(self, full_metadata_path, index_path, metadata, specs, ws_path):
        idx_path = os.path.join(index_path, 'metadata', self._spec)
        log.debug(output_messages['DEBUG_COMMIT_SPEC'] % self._spec, class_name=METADATA_CLASS_NAME)
        # saves README.md if any
        readme = 'README.md'
        src_readme = os.path.join(idx_path, readme)
        self._copy_to_metadata_path(src_readme, full_metadata_path, 'README.md')
        src_ignore_path = os.path.join(idx_path, MLGIT_IGNORE_FILE_NAME)
        self._copy_to_metadata_path(src_ignore_path, full_metadata_path, MLGIT_IGNORE_FILE_NAME)
        amount, workspace_size = self._get_amount_and_size_of_workspace_files(full_metadata_path, ws_path)
        # saves metadata and commit

        entity_spec_key = get_spec_key(self.__repo_type)
        metadata[entity_spec_key]['manifest']['files'] = MANIFEST_FILE
        metadata[entity_spec_key]['manifest']['size'] = humanize.naturalsize(workspace_size)
        metadata[entity_spec_key]['manifest']['amount'] = amount
        storage = metadata[entity_spec_key]['manifest'][STORAGE_SPEC_KEY]

        manifest = metadata[entity_spec_key]['manifest']
        PluginCaller(manifest).call(ADD_METADATA, ws_path, manifest)

        # Add metadata specific to labels ML entity type
        self._add_associate_entity_metadata(metadata, specs)
        self.__commit_spec(full_metadata_path, metadata)

        return storage

    def _add_associate_entity_metadata(self, metadata, specs):
        dataset = EntityType.DATASETS.value
        labels = EntityType.LABELS.value
        model = EntityType.MODELS.value
        entity_spec_key = get_spec_key(self.__repo_type)
        if dataset in specs and self.__repo_type in [labels, model]:
            d_spec = specs[dataset]
            refs_path = get_refs_path(self.__config, dataset)
            r = Refs(refs_path, d_spec, dataset)
            tag, sha = r.head()
            if tag is not None:
                log.info(output_messages['INFO_ASSOCIATE_DATASETS'] % (d_spec, tag, self.__repo_type),
                         class_name=LOCAL_REPOSITORY_CLASS_NAME)
                metadata[entity_spec_key][DATASET_SPEC_KEY] = {}
                metadata[entity_spec_key][DATASET_SPEC_KEY]['tag'] = tag
                metadata[entity_spec_key][DATASET_SPEC_KEY]['sha'] = sha
        if labels in specs and self.__repo_type in [model]:
            l_spec = specs[labels]
            refs_path = get_refs_path(self.__config, labels)
            r = Refs(refs_path, l_spec, labels)
            tag, sha = r.head()
            if tag is not None:
                log.info(
                    'Associate labels [%s]-[%s] to the %s.' % (l_spec, tag, self.__repo_type),
                    class_name=LOCAL_REPOSITORY_CLASS_NAME)
                metadata[entity_spec_key][LABELS_SPEC_KEY] = {}
                metadata[entity_spec_key][LABELS_SPEC_KEY]['tag'] = tag
                metadata[entity_spec_key][LABELS_SPEC_KEY]['sha'] = sha

    def _get_amount_and_size_of_workspace_files(self, full_metadata_path, ws_path):
        full_path = os.path.join(full_metadata_path, MANIFEST_FILE)
        metadata_file = yaml_load(full_path)
        amount = 0
        workspace_size = 0
        for values in metadata_file.values():
            for file_name in values:
                if os.path.exists(normalize_path(os.path.join(ws_path, str(file_name)))):
                    amount += 1
                    workspace_size += get_file_size(normalize_path(os.path.join(ws_path, str(file_name))))
        return amount, workspace_size

    def __commit_spec(self, full_metadata_path, metadata):
        spec_file = self._spec + SPEC_EXTENSION

        # saves yaml metadata specification
        dst_spec_file = os.path.join(full_metadata_path, spec_file)

        yaml_save(metadata, dst_spec_file)

        return True

    def __metadata_spec(self, metadata, sep):
        repo_type = self.__repo_type
        entity_sepc_key = get_spec_key(repo_type)
        cats = metadata[entity_sepc_key]['categories']
        if cats is None:
            log.error(output_messages['ERROR_ENTITY_NEEDS_CATATEGORY'])
            return
        elif type(cats) is list:
            categories = sep.join(cats)
        else:
            categories = cats

        # Generate Spec from Dataset Name & Categories
        try:
            return sep.join([categories, metadata[entity_sepc_key]['name']])
        except Exception:
            log.error(output_messages['ERROR_INVALID_DATASET_SPEC']
                      % (get_sample_spec_doc('somebucket', entity_sepc_key)))
            return None

    def metadata_tag(self, metadata):
        repo_type = self.__repo_type
        entity_spec_key = get_spec_key(repo_type)
        sep = '__'
        tag = self.__metadata_spec(metadata, sep)

        tag = sep.join([tag, str(metadata[entity_spec_key]['version'])])

        log.debug(output_messages['DEBUG_NEW_TAG_CREATED'] % tag, class_name=METADATA_CLASS_NAME)
        return tag

    def metadata_message(self, metadata):
        message = self.metadata_subpath(metadata)

        return message

    def clone_config_repo(self):
        DATASETS = EntityType.DATASETS.value
        MODELS = EntityType.MODELS.value
        LABELS = EntityType.LABELS.value
        dataset = self.__config[DATASETS]['git'] if DATASETS in self.__config else ''
        model = self.__config[MODELS]['git'] if MODELS in self.__config else ''
        labels = self.__config[LABELS]['git'] if LABELS in self.__config else ''

        if not (dataset or model or labels):
            log.error(output_messages['ERROR_REPOSITORY_NOT_FOUND'], class_name=METADATA_CLASS_NAME)
            clear(ROOT_FILE_NAME)
            return

        if dataset:
            self.initialize_metadata(DATASETS)
        if model:
            self.initialize_metadata(MODELS)
        if labels:
            self.initialize_metadata(LABELS)

        log.info(output_messages['INFO_SUCCESS_LOAD_CONFIGURATION'], class_name=METADATA_CLASS_NAME)

    def initialize_metadata(self, entity_type):
        super(Metadata, self).__init__(self.__config, entity_type)
        try:
            self.init()
        except Exception as e:
            log.warn(output_messages['WARN_CANNOT_INITIALIZE_METADATA_FOR'] % (entity_type, e), class_name=METADATA_CLASS_NAME)

    @staticmethod
    def _get_target_tag(tags, target_version):
        tags_versions = {}
        for tag in tags:
            splitted_tag = tag.split('__')
            version = splitted_tag[-1]
            entity = splitted_tag[-2]
            categories_path = splitted_tag[:-2]
            if (target_version == int(version)) or (target_version == -1):
                tags_versions['__'.join(categories_path)] = entity + '__' + version

        if len(tags_versions) > 1:
            result = output_messages['ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME']
            for target_tag in tags_versions:
                result += ('\t' + target_tag + '__' + tags_versions[target_tag] + '\n')
            raise RuntimeError(result)
        elif len(tags_versions) == 0:
            raise RuntimeError(output_messages['ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT'] % tags[-1])

        tag, version = tags_versions.popitem()
        return tag + '__' + version

    def get_tag(self, entity, version):
        try:
            tags = self.list_tags(entity)
            if len(tags) == 0:
                raise RuntimeError(output_messages['ERROR_WITHOUT_TAG_FOR_THIS_ENTITY'])
            target_tag = self._get_target_tag(tags, version)
            if version == -1:
                log.info(output_messages['INFO_CHECKOUT_LATEST_TAG'] % target_tag, class_name=METADATA_CLASS_NAME)
            else:
                log.info(output_messages['INFO_CHECKOUT_TAG'] % target_tag, class_name=METADATA_CLASS_NAME)
            return target_tag
        except RuntimeError as e:
            log.error(e, class_name=METADATA_CLASS_NAME)
            return None

    def get_last_tag_version(self, entity):
        tags = self.list_tags(entity)
        if len(tags) == 0:
            return 0
        last_version = -1
        last_tag = self._get_target_tag(tags, last_version)
        last_version = last_tag.split('__')[-1]
        return int(last_version)

    def get_unpublished_commits_quantity(self):
        try:
            repo = Repo(self.__path)
            active_branch = repo.active_branch
            benchmark = '{0}@{{u}}..{0}'.format(active_branch)
            if active_branch.name not in repo.remote().refs:
                benchmark = 'HEAD'
            unpublished_commits = list(repo.iter_commits(benchmark))
        except GitError as e:
            log.debug(output_messages['DEBUG_UNPUBLISHED_COMMITS'] % (self.__repo_type, e), class_name=METADATA_CLASS_NAME)
            unpublished_commits = []
        quantity = len(unpublished_commits)
        return quantity
