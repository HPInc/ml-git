"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil

from halo import Halo
from hurry.filesize import alternative, size

from ml_git import log
from ml_git._metadata import MetadataManager
from ml_git.config import get_refs_path, get_sample_spec_doc
from ml_git.constants import METADATA_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME, ROOT_FILE_NAME, Mutability
from ml_git.manifest import Manifest
from ml_git.ml_git_message import output_messages
from ml_git.refs import Refs
from ml_git.utils import ensure_path_exists, yaml_save, yaml_load, clear, get_file_size, normalize_path


class Metadata(MetadataManager):
    def __init__(self, spec, metadata_path, config, repo_type='dataset'):
        self.__repo_type = repo_type
        self._spec = spec
        self.__path = metadata_path
        self.__config = config
        super(Metadata, self).__init__(config, repo_type)

    def tag_exists(self, index_path):
        spec_file = os.path.join(index_path, 'metadata', self._spec, self._spec + '.spec')
        full_metadata_path, categories_sub_path, metadata = self._full_metadata_path(spec_file)
        if metadata is None:
            return full_metadata_path, categories_sub_path, metadata

        # generates a tag to associate to the commit
        tag = self.metadata_tag(metadata)

        # check if tag already exists in the ml-git repository
        tags = self._tag_exists(tag)
        if len(tags) > 0:
            log.error(output_messages['ERROR_TAG_ALREADY_EXISTS_VERSION_NUMBER']
                      % (tag, self.__repo_type), class_name=METADATA_CLASS_NAME)
            return None, None, None
        return full_metadata_path, categories_sub_path, metadata

    def commit_metadata(self, index_path, tags, commit_msg, changed_files, mutability, ws_path):
        spec_file = os.path.join(index_path, 'metadata', self._spec, self._spec + '.spec')
        full_metadata_path, categories_sub_path, metadata = self._full_metadata_path(spec_file)
        log.debug(output_messages['DEBUG_METADATA_PATH'] % full_metadata_path, class_name=METADATA_CLASS_NAME)

        if full_metadata_path is None:
            return None, None
        elif categories_sub_path is None:
            return None, None

        ensure_path_exists(full_metadata_path)

        ret = self.__commit_manifest(full_metadata_path, index_path, changed_files, mutability)
        if ret is False:
            log.info(output_messages['INFO_NO_FILES_TO_COMMIT'] % self._spec, class_name=METADATA_CLASS_NAME)
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
            log.error(output_messages['ERROR_TAG_ALREADY_EXISTS'] % tag, class_name=METADATA_CLASS_NAME)
            for t in tags:
                log.error('\t%s' % t)
            return None, None

        if commit_msg is not None and len(commit_msg) > 0:
            msg = commit_msg
        else:
            # generates a commit message
            msg = self.metadata_message(metadata)
        log.debug(output_messages['DEBUG_COMMIT_MESSAGE'] % msg, class_name=METADATA_CLASS_NAME)
        sha = self.commit(categories_sub_path, msg)
        self.tag_add(tag)
        return str(tag), str(sha)

    def metadata_subpath(self, metadata):
        sep = os.sep
        path = self.__metadata_spec(metadata, sep)
        log.debug(output_messages['DEBUG_DATASET_PATH'] % path, class_name=METADATA_CLASS_NAME)
        return path

    def _full_metadata_path(self, spec_file):
        log.debug(output_messages['DEBUG_GETTING_SUBPATH_FROM_CATEGORIES'] % spec_file, class_name=METADATA_CLASS_NAME)

        metadata = yaml_load(spec_file)
        if metadata == {}:
            log.error(output_messages['ERROR_ENTITY_NAME_PASSED_WRONG'], class_name=METADATA_CLASS_NAME)
            return None, None, None
        categories_path = self.metadata_subpath(metadata)
        if categories_path is None:
            log.error(output_messages['ERROR_MUST_PLACE_AT_LEAST_ONE_CATEGORY'], class_name=METADATA_CLASS_NAME)
            return None, None, None

        full_metadata_path = os.path.join(self.__path, categories_path)
        return full_metadata_path, categories_path, metadata

    @Halo(text='Commit manifest', spinner='dots')
    def __commit_manifest(self, full_metadata_path, index_path, changed_files, mutability):
        # Append index/files/MANIFEST.yaml to .ml-git/dataset/metadata/ <categories>/MANIFEST.yaml
        idx_path = os.path.join(index_path, 'metadata', self._spec, 'MANIFEST.yaml')
        if os.path.exists(idx_path) is False:
            log.error(output_messages['ERROR_NO_MANIFEST_FILE_FOUND'] % idx_path, class_name=METADATA_CLASS_NAME)
            return False
        full_path = os.path.join(full_metadata_path, 'MANIFEST.yaml')
        mobj = Manifest(full_path)
        if mutability == Mutability.MUTABLE.value or mutability == Mutability.FLEXIBLE.value:
            for key, file in changed_files:
                mobj.rm(key, file)
        mobj.merge(idx_path)
        mobj.save()
        del (mobj)
        os.unlink(idx_path)
        return True

    def spec_split(self, spec):
        return spec.split('__')

    def get_metadata_path(self, tag):
        specs = self.spec_split(tag)
        categories_path = os.sep.join(specs[:-1])
        return os.path.join(self.__path, categories_path)

    def __commit_metadata(self, full_metadata_path, index_path, metadata, specs, ws_path):
        idx_path = os.path.join(index_path, 'metadata', self._spec)
        log.debug(output_messages['DEBUG_COMMIT_SPEC'] % self._spec, class_name=METADATA_CLASS_NAME)
        # saves README.md if any
        readme = 'README.md'
        src_readme = os.path.join(idx_path, readme)
        if os.path.exists(src_readme):
            dst_readme = os.path.join(full_metadata_path, readme)
            try:
                shutil.copy2(src_readme, dst_readme)
            except Exception as e:
                log.error(output_messages['ERROR_COULD_NOT_FIND_README'], class_name=METADATA_CLASS_NAME)
                raise e
        amount, workspace_size = self._get_amount_and_size_of_workspace_files(full_metadata_path, ws_path)
        # saves metadata and commit
        metadata[self.__repo_type]['manifest']['files'] = 'MANIFEST.yaml'
        metadata[self.__repo_type]['manifest']['size'] = size(workspace_size, system=alternative)
        metadata[self.__repo_type]['manifest']['amount'] = amount
        store = metadata[self.__repo_type]['manifest']['store']
        # Add metadata specific to labels ML entity type
        self._add_associate_entity_metadata(metadata, specs)
        self.__commit_spec(full_metadata_path, metadata)

        return store

    def _add_associate_entity_metadata(self, metadata, specs):
        if 'dataset' in specs and self.__repo_type in ['labels', 'model']:
            d_spec = specs['dataset']
            refs_path = get_refs_path(self.__config, 'dataset')
            r = Refs(refs_path, d_spec, 'dataset')
            tag, sha = r.head()
            if tag is not None:
                log.info(output_messages['INFO_ASSOCIATE_ENTITIES'] % ('dataset', d_spec, tag, self.__repo_type), class_name=LOCAL_REPOSITORY_CLASS_NAME)
                metadata[self.__repo_type]['dataset'] = {}
                metadata[self.__repo_type]['dataset']['tag'] = tag
                metadata[self.__repo_type]['dataset']['sha'] = sha
        if 'labels' in specs and self.__repo_type in ['model']:
            l_spec = specs['labels']
            refs_path = get_refs_path(self.__config, 'labels')
            r = Refs(refs_path, l_spec, 'labels')
            tag, sha = r.head()
            if tag is not None:
                log.info(output_messages['INFO_ASSOCIATE_ENTITIES'] % ('labels', l_spec, tag, self.__repo_type), class_name=LOCAL_REPOSITORY_CLASS_NAME)
                metadata[self.__repo_type]['labels'] = {}
                metadata[self.__repo_type]['labels']['tag'] = tag
                metadata[self.__repo_type]['labels']['sha'] = sha

    def _get_amount_and_size_of_workspace_files(self, full_metadata_path, ws_path):
        full_path = os.path.join(full_metadata_path, 'MANIFEST.yaml')
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
        spec_file = self._spec + '.spec'

        # saves yaml metadata specification
        dst_spec_file = os.path.join(full_metadata_path, spec_file)

        yaml_save(metadata, dst_spec_file)

        return True

    def __metadata_spec(self, metadata, sep):
        repo_type = self.__repo_type
        cats = metadata[repo_type]['categories']
        if cats is None:
            log.error(output_messages['ERROR_MUST_PLACE_AT_LEAST_ONE_CATEGORY'])
            return
        elif type(cats) is list:
            categories = sep.join(cats)
        else:
            categories = cats

        # Generate Spec from Dataset Name & Categories
        try:
            return sep.join([categories, metadata[repo_type]['name']])
        except Exception:
            log.error(output_messages['ERROR_INVALID_DATASET_SPEC'] % (get_sample_spec_doc('somebucket', repo_type)))
            return None

    def metadata_tag(self, metadata):
        repo_type = self.__repo_type

        sep = '__'
        tag = self.__metadata_spec(metadata, sep)

        tag = sep.join([tag, str(metadata[repo_type]['version'])])

        log.debug(output_messages['DEBUG_NEW_TAG_CREATED'] % tag, class_name=METADATA_CLASS_NAME)
        return tag

    def metadata_message(self, metadata):
        message = self.metadata_subpath(metadata)

        return message

    def clone_config_repo(self):
        dataset = self.__config['dataset']['git'] if 'dataset' in self.__config else ''
        model = self.__config['model']['git'] if 'model' in self.__config else ''
        labels = self.__config['labels']['git'] if 'labels' in self.__config else ''

        if not (dataset or model or labels):
            log.error(output_messages['ERROR_REPOSITORY_NOT_FOUND'], class_name=METADATA_CLASS_NAME)
            clear(ROOT_FILE_NAME)
            return

        if dataset:
            self.initialize_metadata('dataset')
        if model:
            self.initialize_metadata('model')
        if labels:
            self.initialize_metadata('labels')

        log.info(output_messages['INFO_SUCCESSFULLY_LOAD_FILES'], class_name=METADATA_CLASS_NAME)

    def initialize_metadata(self, entity_type):
        super(Metadata, self).__init__(self.__config, entity_type)
        try:
            self.init()
        except Exception as e:
            log.warn(output_messages['ERROR_COULD_NOT_INITIALIZE_METADATA'] % (entity_type, e), class_name=METADATA_CLASS_NAME)
