"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import re

import yaml
import errno

from mlgit import log
from mlgit.admin import remote_add, store_add, clone_config_repository
from mlgit.config import index_path, objects_path, cache_path, metadata_path, refs_path, \
    validate_config_spec_hash, validate_spec_hash, get_sample_config_spec, get_sample_spec_doc, \
    index_metadata_path, config_load, create_workspace_tree_structure, import_dir, start_wizard_questions
from mlgit.cache import Cache
from mlgit.manifest import Manifest
from mlgit.metadata import Metadata, MetadataManager
from mlgit.refs import Refs
from mlgit.spec import spec_parse, search_spec_file, increment_version_in_spec, get_entity_tag, update_store_spec
from mlgit.tag import UsrTag
from mlgit.utils import yaml_load, ensure_path_exists, yaml_save, get_root_path, get_path_with_categories, \
    RootPathException
from mlgit.local import LocalRepository
from mlgit.index import MultihashIndex, Objects, Status, FullIndex
from mlgit.hashfs import MultihashFS
from mlgit.workspace import remove_from_workspace
from mlgit.constants import REPOSITORY_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME, HEAD, HEAD_1


class Repository(object):
    def __init__(self, config, repotype="dataset"):
        self.__config = config
        self.__repotype = repotype

    '''initializes ml-git repository metadata'''

    def init(self):
        try:
            metadatapath = metadata_path(self.__config)
            m = Metadata("", metadatapath, self.__config, self.__repotype)
            m.init()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def repo_remote_add(self, repotype, mlgit_remote):
        try:
            remote_add(repotype, mlgit_remote)
            self.__config = config_load()
            metadatapath = metadata_path(self.__config)
            m = Metadata("", metadatapath, self.__config, self.__repotype)
            m.remote_set_url(repotype, mlgit_remote)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''Add dir/files to the ml-git index'''

    def add(self, spec, file_path, bumpversion=False, run_fsck=False):
        repotype = self.__repotype

        if not validate_config_spec_hash(self.__config):
            log.error(".ml-git/config.yaml invalid.  It should look something like this:\n%s"
                      % yaml.dump(get_sample_config_spec("somebucket", "someprofile", "someregion")), class_name=REPOSITORY_CLASS_NAME)
            return None

        path, file = None, None
        try:
            refspath = refs_path(self.__config, repotype)
            indexpath = index_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            cachepath = cache_path(self.__config, repotype)
            objectspath = objects_path(self.__config, repotype)

            repo = LocalRepository(self.__config, objectspath, repotype)
            _, deleted, untracked_files, _ = repo.status(spec, log_errors=False)

            if deleted is not None and len(deleted) == 0 and untracked_files is not None and len(untracked_files) == 0:
                log.info("There is no new data to add", class_name=REPOSITORY_CLASS_NAME)
                return None

            ref = Refs(refspath, spec, repotype)
            tag, sha = ref.branch()

            categories_path = get_path_with_categories(tag)

            path, file = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        if path is None:
            return

        spec_path = os.path.join(path, file)
        spec_file = yaml_load(spec_path)

        if not validate_spec_hash(spec_file, self.__repotype):
            log.error(
                "Invalid %s spec in %s.  It should look something like this:\n%s"
                % (self.__repotype, spec_path, get_sample_spec_doc("somebucket", self.__repotype)), class_name=REPOSITORY_CLASS_NAME
            )
            return None

        # Check tag before anything to avoid creating unstable state
        log.debug("Repository: check if tag already exists", class_name=REPOSITORY_CLASS_NAME)

        m = Metadata(spec, metadatapath, self.__config, repotype)

        try:
            m.update()
        except Exception:
            pass

        # get version of current manifest file
        manifest = ""
        if tag is not None:
            m.checkout(tag)
            md_metadatapath = m.get_metadata_path(tag)
            manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
            m.checkout("master")

        try:
            # adds chunks to ml-git Index
            log.info("%s adding path [%s] to ml-git index" % (repotype, path), class_name=REPOSITORY_CLASS_NAME)
            idx = MultihashIndex(spec, indexpath, objectspath)

            idx.add(path, manifest, file_path)

            # create hard links in ml-git Cache
            mf = os.path.join(indexpath, "metadata", spec, "MANIFEST.yaml")
            c = Cache(cachepath, path, mf)
            c.update()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return None

        if bumpversion and not increment_version_in_spec(spec_path, self.__repotype):
            return None
        idx.add_metadata(path, file)

        # Run file check
        if run_fsck:
            self.fsck()

    def branch(self, spec):
        try:
            repotype = self.__repotype
            refspath = refs_path(self.__config, repotype)
            r = Refs(refspath, spec, repotype)
            print(r.branch())
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''prints status of changes in the index and changes not yet tracked or staged'''
    def status(self, spec):
        repotype = self.__repotype
        try:
            objectspath = objects_path(self.__config, repotype)
            repo = LocalRepository(self.__config, objectspath, repotype)
            log.info("%s: status of ml-git index for [%s]" % (repotype, spec), class_name=REPOSITORY_CLASS_NAME)
            new_files, deleted_files, untracked_files, corruped_files   = repo.status(spec)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        if new_files is not None and deleted_files is not None and untracked_files is not None:
            print("Changes to be committed")
            for file in new_files:
                print("\tnew file: %s" % file)

            for file in deleted_files:
                print("\tdeleted: %s" % file)

            print("\nuntracked files")
            for file in untracked_files:
                print("\t%s" % file)

            print("\ncorrupted files")
            for file in corruped_files:
                print("\t%s" % file)
    '''commit changes present in the ml-git index to the ml-git repository'''
    def commit(self, spec, specs, run_fsck=False, msg=None):
        # Move chunks from index to .ml-git/objects
        repotype = self.__repotype
        try:
            indexpath = index_path(self.__config, repotype)
            objectspath = objects_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        ref = Refs(refspath, spec, repotype)

        tag, sha = ref.branch()
        categories_path = get_path_with_categories(tag)
        manifestpath = os.path.join(metadatapath, categories_path, spec, "MANIFEST.yaml")
        path, file = None, None
        try:
            path, file = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:

            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if path is None:
            return None, None, None

        # Check tag before anything to avoid creating unstable state
        log.debug("Check if tag already exists", class_name=REPOSITORY_CLASS_NAME)
        m = Metadata(spec, metadatapath, self.__config, repotype)

        fullmetadatapath, categories_subpath, metadata = m.tag_exists(indexpath)
        if metadata is None:
            return None

        log.debug("%s -> %s" % (indexpath, objectspath), class_name=REPOSITORY_CLASS_NAME)
        # commit objects in index to ml-git objects
        o = Objects(spec, objectspath)
        o.commit_index(indexpath)

        idx = MultihashIndex(spec, indexpath, objectspath)
        idx.remove_deleted_files_index_manifest(path)

        fidx = FullIndex(spec, indexpath)
        fidx.remove_deleted_files(path)

        manifest = m.get_metadata_manifest(manifestpath)
        m.remove_deleted_files_meta_manifest(path, manifest)
        # update metadata spec & README.md
        # option --dataset-spec --labels-spec
        tag, sha = m.commit_metadata(indexpath, specs, msg)

        # update ml-git ref spec HEAD == to new SHA-1 / tag
        if tag is None:
            return None
        ref = Refs(refspath, spec, repotype)
        ref.update_head(tag, sha)

        # Run file check
        if run_fsck:
            self.fsck()

        return tag

    def list(self):
        repotype = self.__repotype
        try:
            metadatapath = metadata_path(self.__config, repotype)
            m = Metadata("", metadatapath, self.__config, repotype)
            m.checkout("master")
            m.list(title="ML " + repotype)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def tag(self, spec, usrtag):
        repotype = self.__repotype
        try:
            metadatapath = metadata_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
            r = Refs(refspath, spec, repotype)
            curtag, sha = r.head()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return False

        if curtag is None:
            log.error("No current tag for [%s]. commit first." % spec, class_name=REPOSITORY_CLASS_NAME)
            return False
        utag = UsrTag(curtag, usrtag)

        # Check if usrtag exists before creating it
        log.debug("Check if tag [%s] already exists" % utag, class_name=REPOSITORY_CLASS_NAME)
        m = Metadata(spec, metadatapath, self.__config, repotype)
        if m._usrtag_exists(utag) is True:
            log.error("Tag [%s] already exists." % utag, class_name=REPOSITORY_CLASS_NAME)
            return False

        # ensure metadata repository is at the current tag/sha version
        m = Metadata("", metadatapath, self.__config, repotype)
        m.checkout(curtag)

        # TODO: format to something that could be used for a checkout:
        # format: _._user_.._ + curtag + _.._ + usrtag
        # at checkout with usrtag look for pattern _._ then find usrtag in the list (split on '_.._')
        # adds usrtag to the metadata repository

        m = Metadata(spec, metadatapath, self.__config, repotype)
        try:
            m.tag_add(utag)
        except Exception as e:

            match = re.search("stderr: 'fatal:(.*)'$", e.stderr)
            err = match.group(1)
            log.error(err, class_name=REPOSITORY_CLASS_NAME)
            return
        log.info("Create Tag Successfull", class_name=REPOSITORY_CLASS_NAME)
        # checkout at metadata repository at master version
        m.checkout("master")
        return True

    def list_tag(self, spec):
        repotype = self.__repotype
        try:
            metadatapath = metadata_path(self.__config, repotype)
            m = Metadata(spec, metadatapath, self.__config, repotype)
            for tag in m.list_tags(spec):
                print(tag)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    '''push all data related to a ml-git repository to the LocalRepository git repository and data store'''
    def push(self, spec, retry=2, clear_on_fail=False):
        repotype = self.__repotype
        try:
            objectspath = objects_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        met = Metadata(spec, metadatapath, self.__config, repotype)
        fields = met.git_user_config()
        if None in fields.values():
            log.error("Your name and email address need to be configured in git. "
                      "Please see the commands below:", class_name=REPOSITORY_CLASS_NAME)

            log.error('git config --global user.name "Your Name"', class_name=REPOSITORY_CLASS_NAME)
            log.error('git config --global user.email you@example.com"', class_name=REPOSITORY_CLASS_NAME)
            return
        if met.fetch() is False:
            return

        ref = Refs(refspath, spec, repotype)
        tag, sha = ref.branch()
        categories_path = get_path_with_categories(tag)

        specpath, specfile = None, None
        try:
            specpath, specfile = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if specpath is None:
            return

        fullspecpath = os.path.join(specpath, specfile)

        repo = LocalRepository(self.__config, objectspath, repotype)
        ret = repo.push(objectspath, fullspecpath, retry, clear_on_fail)

        # ensure first we're on master !
        met.checkout("master")
        if ret == 0:
            # push metadata spec to LocalRepository git repository
            try:
                met.push()
            except Exception as e:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)
                return
            MultihashFS(objectspath).reset_log()

    '''Retrieves only the metadata related to a ml-git repository'''

    def update(self):
        repotype = self.__repotype
        try:
            metadatapath = metadata_path(self.__config, repotype)
            m = Metadata("", metadatapath, self.__config, repotype)
            m.update()
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

    '''Retrieve only the data related to a specific ML entity version'''

    def _fetch(self, tag, samples, retries=2):
        repotype = self.__repotype
        try:
            objectspath = objects_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            # check if no data left untracked/uncommitted. othrewise, stop.
            local_rep = LocalRepository(self.__config, objectspath, repotype)
            return local_rep.fetch(metadatapath, tag, samples, retries)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

    def fetch_tag(self, tag, samples, retries=2):
        repotype = self.__repotype
        try:
            objectspath = objects_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            m = Metadata("", metadatapath, self.__config, repotype)
            m.checkout(tag)

            fetch_success = self._fetch(tag, samples, retries)

            if not fetch_success:
                objs = Objects("", objectspath)
                objs.fsck(remove_corrupted=True)
                m.checkout("master")
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        # restore to master/head
        self._checkout_ref("master")

    def _checkout_ref(self, ref):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)

        # checkout
        m = Metadata("", metadatapath, self.__config, repotype)
        m.checkout(ref)

    '''Performs fsck on several aspects of ml-git filesystem.
        TODO: add options like following:
        * detect:
            ** fast: performs checks on all blobs present in index / objects
            ** thorough: perform check on files within cache
        * fix:
            ** download again corrupted blob
            ** rebuild cache  
    '''

    def fsck(self):
        repotype = self.__repotype
        try:
            objectspath = objects_path(self.__config, repotype)
            indexpath = index_path(self.__config, repotype)
        except RootPathException:
            return
        o = Objects("", objectspath)
        corrupted_files_obj = o.fsck()
        corrupted_files_obj_len = len(corrupted_files_obj)

        idx = MultihashIndex("", indexpath, objectspath)
        corrupted_files_idx = idx.fsck()
        corrupted_files_idx_len = len(corrupted_files_idx)

        print("[%d] corrupted file(s) in Local Repository: %s" % (corrupted_files_obj_len, corrupted_files_obj))
        print("[%d] corrupted file(s) in Index: %s" % (corrupted_files_idx_len, corrupted_files_idx))
        print("Total of corrupted files: %d" % (corrupted_files_obj_len + corrupted_files_idx_len))

    def show(self, spec):
        repotype = self.__repotype
        try:
            metadatapath = metadata_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return
        r = Refs(refspath, spec, repotype)
        tag, sha = r.head()
        if tag is None:
            log.info("No HEAD for [%s]" % spec, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return

        m = Metadata("", metadatapath, self.__config, repotype)

        m.checkout(tag)

        m.show(spec)

        m.checkout("master")

    def _tag_exists(self, tag):
        md = MetadataManager(self.__config, self.__repotype)
        # check if tag already exists in the ml-git repository
        tags = md._tag_exists(tag)
        if len(tags) == 0:
            log.error("Tag [%s] does not exist in this repository" % tag, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def checkout(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False):
        metadatapath = metadata_path(self.__config)
        dt_tag, lb_tag = self._checkout(tag, samples, retries, force_get, dataset, labels)
        if dt_tag is not None:
            try:
                self.__repotype = "dataset"
                m = Metadata("", metadatapath, self.__config, self.__repotype)
                log.info("Initializing related dataset download", class_name=REPOSITORY_CLASS_NAME)
                if not m.check_exists():
                    m.init()
                self._checkout(dt_tag, samples, retries, force_get, False, False)
            except Exception as e:
                log.error("LocalRepository: [%s]" % e, class_name=REPOSITORY_CLASS_NAME)
        if lb_tag is not None:
            try:
                self.__repotype = "labels"
                m = Metadata("", metadatapath, self.__config, self.__repotype)
                log.info("Initializing related labels download", class_name=REPOSITORY_CLASS_NAME)
                if not m.check_exists():
                    m.init()
                self._checkout(lb_tag, samples, retries, force_get, False, False)
            except Exception as e:
                log.error("LocalRepository: [%s]" % e, class_name=REPOSITORY_CLASS_NAME)

    '''Performs a fsck on remote store w.r.t. some specific ML artefact version'''

    def remote_fsck(self, spec, retries=2, thorough=False, paranoid=False):
        repotype = self.__repotype
        try:

            metadatapath = metadata_path(self.__config, repotype)
            objectspath = objects_path(self.__config, repotype)

            refspath = refs_path(self.__config, repotype)

            ref = Refs(refspath, spec, repotype)
            tag, sha = ref.branch()

            categories_path = get_path_with_categories(tag)

            self._checkout_ref(tag)
            specpath, specfile = search_spec_file(self.__repotype, spec, categories_path)

        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return
        if specpath is None:
            return

        fullspecpath = os.path.join(specpath, specfile)

        r = LocalRepository(self.__config, objectspath, repotype)

        r.remote_fsck(metadatapath, tag, fullspecpath, retries, thorough, paranoid)

        # ensure first we're on master !
        self._checkout_ref("master")

    '''Download data from a specific ML entity version into the workspace'''

    def _checkout(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False):
        repotype = self.__repotype
        try:
            cachepath = cache_path(self.__config, repotype)
            metadatapath = metadata_path(self.__config, repotype)
            objectspath = objects_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
            # find out actual workspace path to save data
            categories_path, specname, _ = spec_parse(tag)
            dataset_tag = None
            labels_tag = None
            root_path = get_root_path()
            wspath = os.path.join(root_path, os.sep.join([repotype, categories_path]))
            if not self._tag_exists(tag):
                return None, None
            ensure_path_exists(wspath)

        except Exception as e:
            log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return None, None

        ref = Refs(refspath, specname, repotype)
        curtag, _ = ref.branch()

        if curtag == tag:
            log.info("already at tag [%s]" % tag, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        local_rep = LocalRepository(self.__config, objectspath, repotype)
        # check if no data left untracked/uncommitted. otherwise, stop.
        if not force_get and local_rep.exist_local_changes(specname) is True:
            return None, None

        try:
            self._checkout_ref(tag)
        except:
            log.error("Unable to checkout to %s" % tag,class_name=REPOSITORY_CLASS_NAME)
            return None, None

        specpath = os.path.join(metadatapath, categories_path, specname + '.spec')

        if dataset is True:
            dataset_tag = get_entity_tag(specpath, repotype, 'dataset')
        if labels is True:
            labels_tag = get_entity_tag(specpath, repotype, 'labels')

        fetch_success = self._fetch(tag, samples, retries)

        if not fetch_success:
            objs = Objects("", objectspath)
            objs.fsck(remove_corrupted=True)
            self._checkout_ref("master")
            return None, None

        try:
            spec_index_path = os.path.join(index_metadata_path(self.__config, repotype), specname)
        except:
            return
        if os.path.exists(spec_index_path):
            if os.path.exists(os.path.join(spec_index_path, specname + ".spec")):
                os.unlink(os.path.join(spec_index_path, specname + ".spec"))
            if os.path.exists(os.path.join(spec_index_path, "README.md")):
                os.unlink(os.path.join(spec_index_path, "README.md"))

        try:
            r = LocalRepository(self.__config, objectspath, repotype)
            r.checkout(cachepath, metadatapath, objectspath, wspath, tag, samples)
        except OSError as e:
            self._checkout_ref("master")
            if e.errno == errno.ENOSPC:
                log.error("There is not enough space in the disk. Remove some files and try again.", class_name=REPOSITORY_CLASS_NAME)
            else:
                log.error("An error occurred while creating the files into workspace: %s \n." % e, class_name=REPOSITORY_CLASS_NAME)
                return None, None
        except Exception as e:
            self._checkout_ref("master")
            log.error("An error occurred while creating the files into workspace: %s \n." % e, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        m = Metadata("", metadatapath, self.__config, repotype)
        sha = m.sha_from_tag(tag)
        ref.update_head(tag, sha)

        # restore to master/head
        self._checkout_ref("master")
        return dataset_tag, labels_tag

    def reset(self, spec, reset_type, head):
        log.info("Initializing reset [%s] [%s] of commit. " % (reset_type, head), class_name=REPOSITORY_CLASS_NAME)
        if (reset_type == '--soft' or reset_type == '--mixed') and head == HEAD:
            return
        try:
            repotype = self.__repotype
            metadatapath = metadata_path(self.__config, repotype)
            indexpath = index_path(self.__config, repotype)
            refspath = refs_path(self.__config, repotype)
            objectpath = objects_path(self.__config, repotype)
            met = Metadata(spec, metadatapath, self.__config, repotype)
            ref = Refs(refspath, spec, repotype)
            idx = MultihashIndex(spec, indexpath, objectpath)
            fidx = FullIndex(spec, indexpath)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return

        # get tag before reset
        tag = met.get_current_tag()
        categories_path = get_path_with_categories(str(tag))
        # current manifest file before reset
        manifestpath = os.path.join(metadatapath, categories_path, spec, "MANIFEST.yaml")
        _manifest = Manifest(manifestpath).load()

        if head == HEAD_1:  # HEAD~1
            try:
                # reset the repo
                met.reset()
            except:
                return

        # get tag after reset
        tag_after_reset = met.get_current_tag()
        sha = met.sha_from_tag(tag_after_reset)

        # update ml-git ref HEAD
        ref.update_head(str(tag_after_reset), sha)

        # # get path to reset workspace in case of --hard
        path, file = None, None
        try:
            path, file = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if reset_type == '--hard' and path is None:
            return

        # get manifest from metadata after reset
        _manifest_changed = Manifest(manifestpath)

        hash_files, filenames = _manifest_changed.get_diff(_manifest)
        idx_mf = idx.get_index().load()

        if reset_type == '--soft':
            # add in index/metadata/<entity-name>/MANIFEST
            idx.update_index_manifest(idx_mf)
            idx.update_index_manifest(hash_files)
            fidx.update_index_status(filenames, Status.a.name)

        else:  # --hard or --mixed
            # remove hash from index/hashsh/store.log
            filenames.update(*idx_mf.values())
            objs = MultihashFS(indexpath)
            for key_hash in hash_files:
                objs.remove_hash(key_hash)
            idx.remove_manifest()
            fidx.remove_from_index_yaml(filenames)
            fidx.remove_uncommitted()

        if reset_type == '--hard':  # reset workspace
            remove_from_workspace(filenames, path, spec)

    def import_files(self, object, path, directory, retry, bucket_name, profile, region):

        err_msg = "Invalid ml-git project!"

        try:
           root = get_root_path()
           root_dir = os.path.join(root, directory)
        except Exception:
            log.error(err_msg, class_name=REPOSITORY_CLASS_NAME)
            return

        local = LocalRepository(self.__config, objects_path(self.__config, self.__repotype), self.__repotype)

        try:
            local.import_files(object,  path, root_dir, retry, bucket_name, profile, region)
        except Exception as e:
            log.error("Fatal downloading error [%s]" % e, class_name=REPOSITORY_CLASS_NAME)

    def create(self, artefact_name, categories, store_type, bucket_name, version, imported_dir, start_wizard):

        repotype = self.__repotype

        try:
            create_workspace_tree_structure(repotype, artefact_name, categories, store_type, bucket_name, version, imported_dir)
        except Exception as e:
            log.error(e, CLASS_NAME=REPOSITORY_CLASS_NAME)
            return

        if start_wizard:

            has_new_store, store_type, bucket, profile, endpoint_url, git_repo = start_wizard_questions(repotype)

            if has_new_store:
                store_add(store_type, bucket, profile, endpoint_url)

            update_store_spec(repotype, artefact_name, store_type, bucket)
            remote_add(repotype, git_repo)

        print('Project Created.')

    def clone_config(self, url, folder, track=False):
        if clone_config_repository(url, folder, track):
            self.__config = config_load()
            m = Metadata("", metadata_path(self.__config), self.__config)
            m.clone_config_repo()


if __name__ == "__main__":
    from mlgit.config import config_load

    config = config_load()
    r = Repository(config)
    r.init()
    r.add("dataset-ex")
    r.commit("dataset-ex")
    r.status("dataset-ex")
