"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import errno
import os
import re

from git import InvalidGitRepositoryError, GitError
from halo import Halo
from hurry.filesize import alternative, size

from ml_git import log
from ml_git.admin import remote_add, store_add, clone_config_repository
from ml_git.file_system.cache import Cache
from ml_git.config import get_index_path, get_objects_path, get_cache_path, get_metadata_path, get_refs_path, \
    validate_config_spec_hash, validate_spec_hash, get_sample_config_spec, get_sample_spec_doc, \
    get_index_metadata_path, create_workspace_tree_structure, start_wizard_questions, config_load
from ml_git.constants import REPOSITORY_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME, HEAD, HEAD_1, Mutability, StoreType
from ml_git.file_system.hashfs import MultihashFS
from ml_git.file_system.index import MultihashIndex, Objects, Status, FullIndex
from ml_git.file_system.local import LocalRepository
from ml_git.manifest import Manifest
from ml_git.metadata import Metadata, MetadataManager
from ml_git.refs import Refs
from ml_git.spec import spec_parse, search_spec_file, increment_version_in_spec, get_entity_tag, update_store_spec, \
    validate_bucket_name, set_version_in_spec
from ml_git.tag import UsrTag
from ml_git.utils import yaml_load, ensure_path_exists, get_root_path, get_path_with_categories, \
    RootPathException, change_mask_for_routine, clear, get_yaml_str, unzip_files_in_directory, remove_from_workspace


class Repository(object):
    def __init__(self, config, repo_type='dataset'):
        self.__config = config
        self.__repo_type = repo_type

    '''initializes ml-git repository metadata'''

    def init(self):
        try:
            metadata_path = get_metadata_path(self.__config)
            m = Metadata('', metadata_path, self.__config, self.__repo_type)
            m.init()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def repo_remote_add(self, repo_type, mlgit_remote, global_conf=False):
        try:
            remote_add(repo_type, mlgit_remote, global_conf)
            self.__config = config_load()
            metadata_path = get_metadata_path(self.__config)
            m = Metadata('', metadata_path, self.__config, self.__repo_type)
            m.remote_set_url(repo_type, mlgit_remote)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''Add dir/files to the ml-git index'''

    def add(self, spec, file_path, bump_version=False, run_fsck=False):
        repo_type = self.__repo_type

        is_shared_objects = 'objects_path' in self.__config[repo_type]
        is_shared_cache = 'cache_path' in self.__config[repo_type]

        if not validate_config_spec_hash(self.__config):
            log.error('.ml-git/config.yaml invalid. It should look something like this:\n%s'
                      % get_yaml_str(get_sample_config_spec('somebucket', 'someprofile', 'someregion')),
                      class_name=REPOSITORY_CLASS_NAME)
            return None

        path, file = None, None
        try:

            refs_path = get_refs_path(self.__config, repo_type)
            index_path = get_index_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            cache_path = get_cache_path(self.__config, repo_type)
            objects_path = get_objects_path(self.__config, repo_type)
            repo = LocalRepository(self.__config, objects_path, repo_type)
            mutability, check_mutability = repo.get_mutability_from_spec(spec, repo_type)
            sampling_flag = os.path.exists(os.path.join(index_path, 'metadata', spec, 'sampling'))
            if sampling_flag:
                log.error('You cannot add new data to an entity that is based on a checkout with the --sampling option.',
                          class_name=REPOSITORY_CLASS_NAME)
                return

            if not mutability:
                return

            if not check_mutability:
                log.error('Spec mutability cannot be changed.', class_name=REPOSITORY_CLASS_NAME)
                return

            _, deleted, untracked_files, _, changed_files = repo.status(spec, log_errors=False)
            if deleted is None and untracked_files is None and changed_files is None:
                return None
            elif len(deleted) == 0 and len(untracked_files) == 0 and len(changed_files) == 0:
                log.info('There is no new data to add', class_name=REPOSITORY_CLASS_NAME)
                return None

            ref = Refs(refs_path, spec, repo_type)
            tag, sha = ref.branch()

            categories_path = get_path_with_categories(tag)

            path, file = search_spec_file(self.__repo_type, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        if path is None:
            return
        spec_path = os.path.join(path, file)
        spec_file = yaml_load(spec_path)

        if not validate_spec_hash(spec_file, self.__repo_type):
            log.error(
                'Invalid %s spec in %s.  It should look something like this:\n%s'
                % (self.__repo_type, spec_path, get_sample_spec_doc('somebucket', self.__repo_type)),
                class_name=REPOSITORY_CLASS_NAME
            )
            return None

        if not validate_bucket_name(spec_file[self.__repo_type], self.__config):
            return None

        # Check tag before anything to avoid creating unstable state
        log.debug('Repository: check if tag already exists', class_name=REPOSITORY_CLASS_NAME)

        m = Metadata(spec, metadata_path, self.__config, repo_type)

        if not m.check_exists():
            log.error('The %s has not been initialized' % self.__repo_type, class_name=REPOSITORY_CLASS_NAME)
            return

        try:
            m.update()
        except Exception:
            pass

        # get version of current manifest file
        manifest = ''
        if tag is not None:
            m.checkout(tag)
            md_metadata_path = m.get_metadata_path(tag)
            manifest = os.path.join(md_metadata_path, 'MANIFEST.yaml')
            m.checkout('master')

        try:
            # adds chunks to ml-git Index
            log.info('%s adding path [%s] to ml-git index' % (repo_type, path), class_name=REPOSITORY_CLASS_NAME)
            with change_mask_for_routine(is_shared_objects):
                idx = MultihashIndex(spec, index_path, objects_path, mutability, cache_path)
                idx.add(path, manifest, file_path)

            # create hard links in ml-git Cache
            self.create_hard_links_in_cache(cache_path, index_path, is_shared_cache, mutability, path, spec)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return None

        if bump_version and not increment_version_in_spec(spec_path, self.__repo_type):
            return None

        idx.add_metadata(path, file)

        self._check_corrupted_files(spec, repo)

        # Run file check
        if run_fsck:
            self.fsck()

    @Halo(text='Creating hard links in cache', spinner='dots')
    def create_hard_links_in_cache(self, cache_path, index_path, is_shared_cache, mutability, path, spec):
        mf = os.path.join(index_path, 'metadata', spec, 'MANIFEST.yaml')
        with change_mask_for_routine(is_shared_cache):
            if mutability in [Mutability.STRICT.value, Mutability.FLEXIBLE.value]:
                cache = Cache(cache_path, path, mf)
                cache.update()

    def _check_corrupted_files(self, spec, repo):
        try:
            corrupted_files = repo.get_corrupted_files(spec)
            if corrupted_files is not None and len(corrupted_files) > 0:
                print('\n')
                log.warn('The following files cannot be added because they are corrupted:',
                         class_name=REPOSITORY_CLASS_NAME)
                for file in corrupted_files:
                    print('\t %s' % file)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def branch(self, spec):
        try:
            repo_type = self.__repo_type
            refs_path = get_refs_path(self.__config, repo_type)
            r = Refs(refs_path, spec, repo_type)
            print(r.branch())
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''prints status of changes in the index and changes not yet tracked or staged'''

    def status(self, spec):
        repo_type = self.__repo_type
        try:
            objects_path = get_objects_path(self.__config, repo_type)
            repo = LocalRepository(self.__config, objects_path, repo_type)
            log.info('%s: status of ml-git index for [%s]' % (repo_type, spec), class_name=REPOSITORY_CLASS_NAME)
            new_files, deleted_files, untracked_files, corruped_files, changed_files = repo.status(spec)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        if new_files is not None and deleted_files is not None and untracked_files is not None:
            print('Changes to be committed:')
            for file in new_files:
                print('\tNew file: %s' % file)

            for file in deleted_files:
                print('\tDeleted: %s' % file)

            print('\nUntracked files:')
            for file in untracked_files:
                print('\t%s' % file)

            print('\nCorrupted files:')
            for file in corruped_files:
                print('\t%s' % file)

            if changed_files and len(changed_files) > 0:
                print('\nChanges not staged for commit:')
                for file in changed_files:
                    print('\t%s' % file)

    '''commit changes present in the ml-git index to the ml-git repository'''

    def commit(self, spec, specs, version_number=None, run_fsck=False, msg=None):
        # Move chunks from index to .ml-git/objects
        repo_type = self.__repo_type
        try:
            index_path = get_index_path(self.__config, repo_type)
            objects_path = get_objects_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
            repo = LocalRepository(self.__config, objects_path, repo_type)
            mutability, check_mutability = repo.get_mutability_from_spec(spec, repo_type)

            if not mutability:
                return

            if not check_mutability:
                log.error('Spec mutability cannot be changed.', class_name=REPOSITORY_CLASS_NAME)
                return
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        ref = Refs(refs_path, spec, repo_type)

        tag, sha = ref.branch()
        categories_path = get_path_with_categories(tag)
        manifest_path = os.path.join(metadata_path, categories_path, spec, 'MANIFEST.yaml')
        path, file = None, None
        try:
            path, file = search_spec_file(self.__repo_type, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if path is None:
            return None, None, None

        spec_path = os.path.join(path, file)
        idx = MultihashIndex(spec, index_path, objects_path)

        if version_number:
            set_version_in_spec(version_number, spec_path, self.__repo_type)
            idx.add_metadata(path, file)

        # Check tag before anything to avoid creating unstable state
        log.debug('Check if tag already exists', class_name=REPOSITORY_CLASS_NAME)
        m = Metadata(spec, metadata_path, self.__config, repo_type)

        if not m.check_exists():
            log.error('The %s has not been initialized' % self.__repo_type, class_name=REPOSITORY_CLASS_NAME)
            return

        full_metadata_path, categories_sub_path, metadata = m.tag_exists(index_path)
        if metadata is None:
            return None

        log.debug('%s -> %s' % (index_path, objects_path), class_name=REPOSITORY_CLASS_NAME)
        # commit objects in index to ml-git objects
        o = Objects(spec, objects_path)
        changed_files, deleted_files = o.commit_index(index_path, path)

        bare_mode = os.path.exists(os.path.join(index_path, 'metadata', spec, 'bare'))

        if not bare_mode and len(deleted_files) > 0:
            self.remove_deleted_files(idx, index_path, m, manifest_path, path, spec, deleted_files)
        elif bare_mode:
            tag, _ = ref.branch()
            self._checkout_ref(tag)
        # update metadata spec & README.md
        # option --dataset-spec --labels-spec
        tag, sha = m.commit_metadata(index_path, specs, msg, changed_files, mutability, path)

        # update ml-git ref spec HEAD == to new SHA-1 / tag
        if tag is None:
            return None
        ref = Refs(refs_path, spec, repo_type)
        ref.update_head(tag, sha)

        # Run file check
        if run_fsck:
            self.fsck()

        return tag

    @Halo(text='Checking removed files', spinner='dots')
    def remove_deleted_files(self, idx, index_path, m, manifest_path, path, spec, deleted_files):
        fidx = FullIndex(spec, index_path)
        manifest = m.get_metadata_manifest(manifest_path)
        fidx.remove_deleted_files(deleted_files)
        idx.remove_deleted_files_index_manifest(deleted_files)
        m.remove_deleted_files_meta_manifest(manifest, deleted_files)

    def list(self):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            m = Metadata('', metadata_path, self.__config, repo_type)
            if not m.check_exists():
                raise RuntimeError('The %s doesn\'t have been initialized.' % self.__repo_type)
            m.checkout('master')
            m.list(title='ML ' + repo_type)
        except GitError as g:
            error_message = g.stderr
            if 'did not match any file(s) known' in error_message:
                error_message = 'You don\'t have any entity being managed.'
            log.error(error_message, class_name=REPOSITORY_CLASS_NAME)
            return
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def tag(self, spec, usr_tag):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
            r = Refs(refs_path, spec, repo_type)
            curtag, sha = r.head()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return False

        if curtag is None:
            log.error('No current tag for [%s]. commit first.' % spec, class_name=REPOSITORY_CLASS_NAME)
            return False
        utag = UsrTag(curtag, usr_tag)

        # Check if usrtag exists before creating it
        log.debug('Check if tag [%s] already exists' % utag, class_name=REPOSITORY_CLASS_NAME)
        m = Metadata(spec, metadata_path, self.__config, repo_type)
        if m._usrtag_exists(utag) is True:
            log.error('Tag [%s] already exists.' % utag, class_name=REPOSITORY_CLASS_NAME)
            return False

        # ensure metadata repository is at the current tag/sha version
        m = Metadata('', metadata_path, self.__config, repo_type)
        m.checkout(curtag)

        # TODO: format to something that could be used for a checkout:
        # format: _._user_.._ + curtag + _.._ + usrtag
        # at checkout with usrtag look for pattern _._ then find usrtag in the list (split on '_.._')
        # adds usrtag to the metadata repository

        m = Metadata(spec, metadata_path, self.__config, repo_type)
        try:
            m.tag_add(utag)
        except Exception as e:

            match = re.search("stderr: 'fatal:(.*)'$", e.stderr)
            err = match.group(1)
            log.error(err, class_name=REPOSITORY_CLASS_NAME)
            return
        log.info('Create Tag Successfull', class_name=REPOSITORY_CLASS_NAME)
        # checkout at metadata repository at master version
        m.checkout('master')
        return True

    def list_tag(self, spec):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            m = Metadata(spec, metadata_path, self.__config, repo_type)
            for tag in m.list_tags(spec):
                print(tag)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''push all data related to a ml-git repository to the LocalRepository git repository and data store'''

    def push(self, spec, retry=2, clear_on_fail=False):
        repo_type = self.__repo_type
        try:
            objects_path = get_objects_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        met = Metadata(spec, metadata_path, self.__config, repo_type)
        fields = met.git_user_config()
        if None in fields.values():
            log.error('Your name and email address need to be configured in git. '
                      'Please see the commands below:', class_name=REPOSITORY_CLASS_NAME)

            log.error('git config --global user.name \'Your Name\'', class_name=REPOSITORY_CLASS_NAME)
            log.error('git config --global user.email you@example.com', class_name=REPOSITORY_CLASS_NAME)
            return
        if met.fetch() is False:
            return

        ref = Refs(refs_path, spec, repo_type)
        tag, sha = ref.branch()
        categories_path = get_path_with_categories(tag)

        spec_path, spec_file = None, None
        try:
            spec_path, spec_file = search_spec_file(self.__repo_type, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if spec_path is None:
            return

        full_spec_path = os.path.join(spec_path, spec_file)

        repo = LocalRepository(self.__config, objects_path, repo_type)
        ret = repo.push(objects_path, full_spec_path, retry, clear_on_fail)

        # ensure first we're on master !
        met.checkout('master')
        if ret == 0:
            # push metadata spec to LocalRepository git repository
            try:
                met.push()
            except Exception as e:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)
                return
            MultihashFS(objects_path).reset_log()

    '''Retrieves only the metadata related to a ml-git repository'''

    def update(self):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            m = Metadata('', metadata_path, self.__config, repo_type)
            m.update()
        except GitError as error:
            log.error('Could not update metadata. Check your remote configuration. %s' % error.stderr, class_name=REPOSITORY_CLASS_NAME)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

    '''Retrieve only the data related to a specific ML entity version'''

    def _fetch(self, tag, samples, retries=2, bare=False):
        repo_type = self.__repo_type
        try:
            objects_path = get_objects_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            # check if no data left untracked/uncommitted. othrewise, stop.
            local_rep = LocalRepository(self.__config, objects_path, repo_type)
            return local_rep.fetch(metadata_path, tag, samples, retries, bare)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def fetch_tag(self, tag, samples, retries=2):
        repo_type = self.__repo_type
        try:
            objects_path = get_objects_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            m = Metadata('', metadata_path, self.__config, repo_type)
            m.checkout(tag)

            fetch_success = self._fetch(tag, samples, retries)

            if not fetch_success:
                objs = Objects('', objects_path)
                objs.fsck(remove_corrupted=True)
                m.checkout('master')
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        # restore to master/head
        self._checkout_ref('master')

    def _checkout_ref(self, ref):
        repo_type = self.__repo_type
        metadata_path = get_metadata_path(self.__config, repo_type)

        # checkout
        m = Metadata('', metadata_path, self.__config, repo_type)
        m.checkout(ref)

    '''Performs fsck on several aspects of ml-git filesystem.
        TODO: add options like following:
        * detect:
            ** fast: performs checks on all blobs present in index / objects
            ** thorough: perform check on files within cache
        * fix:
            ** download again corrupted blob
            ** rebuild cache'''

    def fsck(self):
        repo_type = self.__repo_type
        try:
            objects_path = get_objects_path(self.__config, repo_type)
            index_path = get_index_path(self.__config, repo_type)
        except RootPathException:
            return
        o = Objects('', objects_path)
        corrupted_files_obj = o.fsck()
        corrupted_files_obj_len = len(corrupted_files_obj)

        idx = MultihashIndex('', index_path, objects_path)
        corrupted_files_idx = idx.fsck()
        corrupted_files_idx_len = len(corrupted_files_idx)

        print('[%d] corrupted file(s) in Local Repository: %s' % (corrupted_files_obj_len, corrupted_files_obj))
        print('[%d] corrupted file(s) in Index: %s' % (corrupted_files_idx_len, corrupted_files_idx))
        print('Total of corrupted files: %d' % (corrupted_files_obj_len + corrupted_files_idx_len))

    def show(self, spec):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return
        r = Refs(refs_path, spec, repo_type)
        tag, sha = r.head()
        if tag is None:
            log.info('No HEAD for [%s]' % spec, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return

        m = Metadata('', metadata_path, self.__config, repo_type)

        m.checkout(tag)

        m.show(spec)

        m.checkout('master')

    def _tag_exists(self, tag):
        md = MetadataManager(self.__config, self.__repo_type)
        # check if tag already exists in the ml-git repository
        tags = md._tag_exists(tag)
        if len(tags) == 0:
            log.error('Tag [%s] does not exist in this repository' % tag, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def checkout(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False, bare=False):
        metadata_path = get_metadata_path(self.__config)
        dt_tag, lb_tag = self._checkout(tag, samples, retries, force_get, dataset, labels, bare)
        if dt_tag is not None:
            try:
                self.__repo_type = 'dataset'
                m = Metadata('', metadata_path, self.__config, self.__repo_type)
                log.info('Initializing related dataset download', class_name=REPOSITORY_CLASS_NAME)
                if not m.check_exists():
                    m.init()
                self._checkout(dt_tag, samples, retries, force_get, False, False, bare)
            except Exception as e:
                log.error('LocalRepository: [%s]' % e, class_name=REPOSITORY_CLASS_NAME)
        if lb_tag is not None:
            try:
                self.__repo_type = 'labels'
                m = Metadata('', metadata_path, self.__config, self.__repo_type)
                log.info('Initializing related labels download', class_name=REPOSITORY_CLASS_NAME)
                if not m.check_exists():
                    m.init()
                self._checkout(lb_tag, samples, retries, force_get, False, False, bare)
            except Exception as e:
                log.error('LocalRepository: [%s]' % e, class_name=REPOSITORY_CLASS_NAME)

    '''Performs a fsck on remote store w.r.t. some specific ML artefact version'''

    def remote_fsck(self, spec, retries=2, thorough=False, paranoid=False):
        repo_type = self.__repo_type
        try:
            metadata_path = get_metadata_path(self.__config, repo_type)
            objects_path = get_objects_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
            ref = Refs(refs_path, spec, repo_type)
            tag, sha = ref.branch()

            categories_path = get_path_with_categories(tag)

            self._checkout_ref(tag)
            spec_path, spec_file = search_spec_file(self.__repo_type, spec, categories_path)

        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return
        if spec_path is None:
            return

        full_spec_path = os.path.join(spec_path, spec_file)

        r = LocalRepository(self.__config, objects_path, repo_type)

        r.remote_fsck(metadata_path, tag, full_spec_path, retries, thorough, paranoid)

        # ensure first we're on master !
        self._checkout_ref('master')

    '''Download data from a specific ML entity version into the workspace'''

    def _checkout(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False, bare=False):
        repo_type = self.__repo_type
        try:
            cache_path = get_cache_path(self.__config, repo_type)
            metadata_path = get_metadata_path(self.__config, repo_type)
            objects_path = get_objects_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
            # find out actual workspace path to save data
            if not self._tag_exists(tag):
                return None, None
            categories_path, spec_name, _ = spec_parse(tag)
            dataset_tag = None
            labels_tag = None
            root_path = get_root_path()
            ws_path = os.path.join(root_path, os.sep.join([repo_type, categories_path]))
            ensure_path_exists(ws_path)
        except Exception as e:
            log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return None, None

        ref = Refs(refs_path, spec_name, repo_type)
        cur_tag, _ = ref.branch()

        if cur_tag == tag:
            log.info('already at tag [%s]' % tag, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        local_rep = LocalRepository(self.__config, objects_path, repo_type)
        # check if no data left untracked/uncommitted. otherwise, stop.
        if not force_get and local_rep.exist_local_changes(spec_name) is True:
            return None, None

        try:
            self._checkout_ref(tag)
        except Exception:
            log.error('Unable to checkout to %s' % tag, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        spec_path = os.path.join(metadata_path, categories_path, spec_name + '.spec')

        if dataset is True:
            dataset_tag = get_entity_tag(spec_path, repo_type, 'dataset')
        if labels is True:
            labels_tag = get_entity_tag(spec_path, repo_type, 'labels')

        fetch_success = self._fetch(tag, samples, retries, bare)

        if not fetch_success:
            objs = Objects('', objects_path)
            objs.fsck(remove_corrupted=True)
            self._checkout_ref('master')
            return None, None

        try:
            spec_index_path = os.path.join(get_index_metadata_path(self.__config, repo_type), spec_name)
        except Exception:
            return
        if os.path.exists(spec_index_path):
            if os.path.exists(os.path.join(spec_index_path, spec_name + '.spec')):
                os.unlink(os.path.join(spec_index_path, spec_name + '.spec'))
            if os.path.exists(os.path.join(spec_index_path, 'README.md')):
                os.unlink(os.path.join(spec_index_path, 'README.md'))

        try:
            r = LocalRepository(self.__config, objects_path, repo_type)
            r.checkout(cache_path, metadata_path, objects_path, ws_path, tag, samples, bare)
        except OSError as e:
            self._checkout_ref('master')
            if e.errno == errno.ENOSPC:
                log.error('There is not enough space in the disk. Remove some files and try again.',
                          class_name=REPOSITORY_CLASS_NAME)
            else:
                log.error('An error occurred while creating the files into workspace: %s \n.' % e,
                          class_name=REPOSITORY_CLASS_NAME)
                return None, None
        except Exception as e:
            self._checkout_ref('master')
            log.error('An error occurred while creating the files into workspace: %s \n.' % e,
                      class_name=REPOSITORY_CLASS_NAME)
            return None, None

        m = Metadata('', metadata_path, self.__config, repo_type)
        sha = m.sha_from_tag(tag)
        ref.update_head(tag, sha)

        # restore to master/head
        self._checkout_ref('master')
        return dataset_tag, labels_tag

    def reset(self, spec, reset_type, head):
        log.info('Initializing reset [%s] [%s] of commit. ' % (reset_type, head), class_name=REPOSITORY_CLASS_NAME)
        if (reset_type == '--soft' or reset_type == '--mixed') and head == HEAD:
            return
        try:
            repo_type = self.__repo_type
            metadata_path = get_metadata_path(self.__config, repo_type)
            index_path = get_index_path(self.__config, repo_type)
            refs_path = get_refs_path(self.__config, repo_type)
            object_path = get_objects_path(self.__config, repo_type)
            met = Metadata(spec, metadata_path, self.__config, repo_type)
            ref = Refs(refs_path, spec, repo_type)
            idx = MultihashIndex(spec, index_path, object_path)
            fidx = FullIndex(spec, index_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        # get tag before reset
        tag = met.get_current_tag()
        categories_path = get_path_with_categories(str(tag))
        # current manifest file before reset
        manifest_path = os.path.join(metadata_path, categories_path, spec, 'MANIFEST.yaml')
        _manifest = Manifest(manifest_path).load()

        if head == HEAD_1:  # HEAD~1
            try:
                # reset the repo
                met.reset()
            except Exception:
                return

        # get tag after reset
        tag_after_reset = met.get_current_tag()
        sha = met.sha_from_tag(tag_after_reset)

        # update ml-git ref HEAD
        ref.update_head(str(tag_after_reset), sha)

        # # get path to reset workspace in case of --hard
        path, file = None, None
        try:
            path, file = search_spec_file(self.__repo_type, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if reset_type == '--hard' and path is None:
            return

        # get manifest from metadata after reset
        _manifest_changed = Manifest(manifest_path)

        hash_files, file_names = _manifest_changed.get_diff(_manifest)
        idx_mf = idx.get_index().load()

        if reset_type == '--soft':
            # add in index/metadata/<entity-name>/MANIFEST
            idx.update_index_manifest(idx_mf)
            idx.update_index_manifest(hash_files)
            fidx.update_index_status(file_names, Status.a.name)

        else:  # --hard or --mixed
            # remove hash from index/hashsh/store.log
            file_names.update(*idx_mf.values())
            objs = MultihashFS(index_path)
            for key_hash in hash_files:
                objs.remove_hash(key_hash)
            idx.remove_manifest()
            fidx.remove_from_index_yaml(file_names)
            fidx.remove_uncommitted()

        if reset_type == '--hard':  # reset workspace
            remove_from_workspace(file_names, path, spec)

    def import_files(self, object, path, directory, retry, bucket_name, profile, region, store_type, endpoint_url):

        err_msg = 'Invalid ml-git project!'

        try:
            root = get_root_path()
            root_dir = os.path.join(root, directory)
        except Exception:
            log.error(err_msg, class_name=REPOSITORY_CLASS_NAME)
            return

        local = LocalRepository(self.__config, get_objects_path(self.__config, self.__repo_type), self.__repo_type)
        local.change_config_store(profile, bucket_name, store_type, region=region, endpoint_url=endpoint_url)
        local.import_files(object, path, root_dir, retry, '{}://{}'.format(store_type, bucket_name))

    def unlock_file(self, spec, file_path):
        repo_type = self.__repo_type

        if not validate_config_spec_hash(self.__config):
            log.error('.ml-git/config.yaml invalid.  It should look something like this:\n%s'
                      % get_yaml_str(get_sample_config_spec('somebucket', 'someprofile', 'someregion')),
                      class_name=REPOSITORY_CLASS_NAME)
            return None

        path, file = None, None
        try:
            refs_path = get_refs_path(self.__config, repo_type)
            objects_path = get_objects_path(self.__config, repo_type)
            index_path = get_index_path(self.__config, repo_type)
            cache_path = get_cache_path(self.__config, repo_type)

            ref = Refs(refs_path, spec, repo_type)
            tag, sha = ref.branch()
            categories_path = get_path_with_categories(tag)

            path, file = search_spec_file(self.__repo_type, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        if path is None:
            return

        spec_path = os.path.join(path, file)
        spec_file = yaml_load(spec_path)

        try:
            mutability = spec_file[repo_type]['mutability']
            if mutability not in list(map(lambda c: c.value, Mutability)):
                log.error('Invalid mutability type.', class_name=REPOSITORY_CLASS_NAME)
                return
        except Exception:
            log.info('The spec does not have the \'mutability\' property set. Default: strict.',
                     class_name=REPOSITORY_CLASS_NAME)
            return

        if mutability != Mutability.STRICT.value:
            try:
                local = LocalRepository(self.__config, objects_path, repo_type)
                local.unlock_file(path, file_path, index_path, objects_path, spec, cache_path)
            except Exception as e:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)
                return
        else:
            log.error('You cannot use this command for this entity because mutability cannot be strict.',
                      class_name=REPOSITORY_CLASS_NAME)

    def create_config_store(self, store_type, credentials_path):
        bucket = {'credentials-path': credentials_path}
        self.__config['store'][store_type] = {store_type: bucket}

    def create(self, artifact_name, categories, store_type, bucket_name, version, imported_dir, start_wizard,
               import_url, unzip_file, credentials_path):
        repo_type = self.__repo_type
        try:
            create_workspace_tree_structure(repo_type, artifact_name, categories, store_type, bucket_name, version,
                                            imported_dir)
            if start_wizard:
                has_new_store, store_type, bucket, profile, endpoint_url, git_repo = start_wizard_questions(repo_type)
                if has_new_store:
                    store_add(store_type, bucket, profile, endpoint_url)
                update_store_spec(repo_type, artifact_name, store_type, bucket)
                remote_add(repo_type, git_repo)
            if import_url:
                self.create_config_store('gdrive', credentials_path)
                local = LocalRepository(self.__config, get_objects_path(self.__config, repo_type))
                destine_path = os.path.join(repo_type, artifact_name, 'data')
                local.import_file_from_url(destine_path, import_url, StoreType.GDRIVE.value)
            if unzip_file:
                log.info('Unzipping files', CLASS_NAME=REPOSITORY_CLASS_NAME)
                data_path = os.path.join(get_root_path(), repo_type, artifact_name, 'data')
                unzip_files_in_directory(data_path)
            log.info("Project Created.", CLASS_NAME=REPOSITORY_CLASS_NAME)
        except Exception as e:
            if not isinstance(e, PermissionError):
                clear(os.path.join(repo_type, artifact_name))
            if isinstance(e, KeyboardInterrupt):
                log.info("Create command aborted!", class_name=REPOSITORY_CLASS_NAME)
            else:
                log.error(e, CLASS_NAME=REPOSITORY_CLASS_NAME)

    def clone_config(self, url, folder=None, track=False):
        if clone_config_repository(url, folder, track):
            self.__config = config_load()
            m = Metadata('', get_metadata_path(self.__config), self.__config)
            m.clone_config_repo()

    def export(self, bucket, tag, profile, region, endpoint, retry):
        try:
            categories_path, spec_name, _ = spec_parse(tag)
            get_root_path()
            if not self._tag_exists(tag):
                return None, None
        except InvalidGitRepositoryError:
            log.error('You are not in an initialized ml-git repository.', class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return None, None
        except Exception as e:
            log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return None, None

        try:
            self._checkout_ref(tag)
        except Exception:
            log.error('Unable to checkout to %s' % tag, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        local = LocalRepository(self.__config, get_objects_path(self.__config, self.__repo_type), self.__repo_type)
        local.export_tag(get_metadata_path(self.__config, self.__repo_type), tag, bucket, profile, region, endpoint,
                         retry)

        self._checkout_ref('master')

    def log(self, spec, stat=False, fullstat=False):

        try:
            repo_type = self.__repo_type
            metadata_path = get_metadata_path(self.__config, repo_type)
            metadata = Metadata(spec, metadata_path, self.__config, repo_type)
            index_path = get_index_path(self.__config, repo_type)

            log_info = metadata.get_log_info(spec, fullstat)

        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return
        fidx = FullIndex(spec, index_path)
        if stat or fullstat:
            workspace_size = fidx.get_total_size()

            amount_message = 'Total of files: %s' % fidx.get_total_count()
            size_message = 'Workspace size: %s' % size(workspace_size, system=alternative)

            workspace_info = '------------------------------------------------- \n{}\t{}' \
                .format(amount_message, size_message)

            log_info = '{}\n{}'.format(log_info, workspace_info)

        log.info(log_info, class_name=REPOSITORY_CLASS_NAME)


if __name__ == '__main__':
    config = config_load()
    r = Repository(config)
    r.init()
    r.add('dataset-ex')
    r.commit('dataset-ex')
    r.status('dataset-ex')
