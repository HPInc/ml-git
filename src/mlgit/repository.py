"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import yaml
import errno

from git import Repo

from mlgit import log
from mlgit.admin import remote_add
from mlgit.config import index_path, objects_path, cache_path, metadata_path, refs_path, \
    validate_config_spec_hash, validate_dataset_spec_hash, get_sample_config_spec, get_sample_dataset_spec_doc, \
    index_metadata_path
from mlgit.cache import Cache
from mlgit.metadata import Metadata, MetadataManager
from mlgit.refs import Refs
from mlgit.spec import spec_parse, search_spec_file, increment_version_in_dataset_spec
from mlgit.tag import UsrTag
from mlgit.utils import yaml_load, ensure_path_exists, yaml_save, get_root_path
from mlgit.local import LocalRepository
from mlgit.index import MultihashIndex, Objects
from mlgit.constants import REPOSITORY_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME


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
            log.error(e)

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

    def add(self, spec, bumpversion=False, run_fsck=False, del_files=False):
        if not validate_config_spec_hash(self.__config):
            log.error(".ml-git/config.yaml invalid.  It should look something like this:\n%s"
                      % yaml.dump(get_sample_config_spec("somebucket", "someprofile", "someregion")), class_name=REPOSITORY_CLASS_NAME)
            return None

        tag, sha = self._branch(spec)
        categories_path = self._get_path_with_categories(tag)
        path, file = None, None
        try:
            path, file = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if path is None:
            return

        f = os.path.join(path, file)
        dataset_spec = yaml_load(f)

        if bumpversion and not increment_version_in_dataset_spec(f, self.__repotype):
            return None

        if not validate_dataset_spec_hash(dataset_spec, self.__repotype):
            log.error(
                "Invalid dataset spec in %s.  It should look something like this:\n%s"
                % (f, get_sample_dataset_spec_doc("somebucket")), class_name=REPOSITORY_CLASS_NAME
            )
            return None

        repotype = self.__repotype

        indexpath = index_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)
        cachepath = cache_path(self.__config, repotype)

        # Check tag before anything to avoid creating unstable state
        log.debug("Repository: check if tag already exists")
        m = Metadata(spec, metadatapath, self.__config, repotype)

        # get version of current manifest file
        tag, sha = self._branch(spec)
        manifest = ""
        if tag is not None:
            self._checkout(tag)
            m = Metadata(spec, metadatapath, self.__config, repotype)
            md_metadatapath = m.get_metadata_path(tag)
            manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
            self._checkout("master")

        # Remove deleted files from MANIFEST
        if del_files:
            manifest_files = yaml_load(manifest)

            deleted_files = []
            for k in manifest_files:
                for file in manifest_files[k]:
                    if not os.path.exists(os.path.join(path, file)):
                        deleted_files.append([k,file])

            for file in deleted_files:
                if len(manifest_files[file[0]]) > 1:
                    manifest_files[file[0]].remove(file[1])
                else:
                    del (manifest_files[file[0]])

            yaml_save(manifest_files, manifest)

        # adds chunks to ml-git Index
        log.info("%s adding path [%s] to ml-git index" % (repotype, path), class_name=REPOSITORY_CLASS_NAME)
        idx = MultihashIndex(spec, indexpath)
        idx.add(path, manifest)

        # create hard links in ml-git Cache
        mf = os.path.join(indexpath, "metadata", spec, "MANIFEST.yaml")
        c = Cache(cachepath, path, mf)
        c.update()

        # Run file check
        if run_fsck:
            self.fsck()

    def branch(self, spec):
        print(self._branch(spec))

    def _branch(self, spec):
        repotype = self.__repotype
        refspath = refs_path(self.__config, repotype)
        r = Refs(refspath, spec, repotype)
        return r.head()

    '''prints status of changes in the index and changes not yet tracked or staged'''
    def status(self, spec):
        repotype = self.__repotype

        log.info("%s: status of ml-git index for [%s]" % (repotype, spec), class_name=REPOSITORY_CLASS_NAME)
        new_files, deleted_files, untracked_files = self._status(spec)

        if new_files is not None and deleted_files is not None and untracked_files is not None:
            print("Changes to be committed")
            for file in new_files:
                print("\tnew file: %s" % file)

            for file in deleted_files:
                print("\tdeleted: %s" % file)

            print("\nuntracked files")
            for file in untracked_files:
                print("\t%s" % file)

    '''commit changes present in the ml-git index to the ml-git repository'''
    def commit(self, spec, specs, run_fsck=False):
        # Move chunks from index to .ml-git/objects
        repotype = self.__repotype
        indexpath = index_path(self.__config, repotype)
        objectspath = objects_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)
        refspath = refs_path(self.__config, repotype)

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

        # update metadata spec & README.md
        # option --dataset-spec --labels-spec
        m = Metadata(spec, metadatapath, self.__config, repotype)
        tag, sha = m.commit_metadata(indexpath, specs)

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
        metadatapath = metadata_path(self.__config, repotype)

        self._checkout("master")

        m = Metadata("", metadatapath, self.__config, repotype)
        m.list(title="ML " + repotype)

    def tag(self, spec, usrtag):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)
        refspath = refs_path(self.__config, repotype)

        r = Refs(refspath, spec, repotype)
        curtag, sha = r.head()

        if curtag == None:
            log.error("No current tag for [%s]. commit first." % spec, class_name=REPOSITORY_CLASS_NAME)
            return False
        utag = UsrTag(curtag, usrtag)

        # Check if usrtag exists before creating it
        log.debug("Check if tag [%s] already exists" % utag, class_name=REPOSITORY_CLASS_NAME)
        m = Metadata(spec, metadatapath, self.__config, repotype)
        if m._usrtag_exists(utag) == True:
            log.error("Tag [%s] already exists." % utag, class_name=REPOSITORY_CLASS_NAME)
            return False

        # ensure metadata repository is at the current tag/sha version

        m = Metadata("", metadatapath, self.__config, repotype)
        m.checkout(curtag)

        # print(curtag, utag)
        # TODO: format to something that could be used for a checkout:
        # format: _._user_.._ + curtag + _.._ + usrtag
        # at checkout with usrtag look for pattern _._ then find usrtag in the list (split on '_.._')
        # adds usrtag to the metadata repository

        m = Metadata(spec, metadatapath, self.__config, repotype)
        m.tag_add(utag)

        # checkout at metadata repository at master version
        self._checkout("master")
        return True

    def list_tag(self, spec):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)

        m = Metadata(spec, metadatapath, self.__config, repotype)
        for tag in m.list_tags(spec):
            print(tag)

    '''push all data related to a ml-git repository to the LocalRepository git repository and data store'''
    def push(self, spec, retry=2, clear_on_fail=False):
        repotype = self.__repotype
        indexpath = index_path(self.__config, repotype)
        objectspath = objects_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)

        m = Metadata(spec, metadatapath, self.__config, repotype)
        fields = m.git_user_config()
        if None in fields.values():
            log.error("Your name and email address need to be configured in git. "
                      "Please see the commands below:", class_name=REPOSITORY_CLASS_NAME)

            log.error('git config --global user.name "Your Name"', class_name=REPOSITORY_CLASS_NAME)
            log.error('git config --global user.email you@example.com"', class_name=REPOSITORY_CLASS_NAME)
            return
        if m.fetch() is False:
            return

        tag, sha = self._branch(spec)
        categories_path = self._get_path_with_categories(tag)

        specpath, specfile = None, None
        try:
            specpath, specfile = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if specpath is None:
            return

        fullspecpath = os.path.join(specpath, specfile)

        r = LocalRepository(self.__config, objectspath, repotype)
        ret = r.push(indexpath, objectspath, fullspecpath, retry, clear_on_fail)

        # ensure first we're on master !
        self._checkout("master")
        if ret == 0:
            # push metadata spec to LocalRepository git repository
            m = Metadata(spec, metadatapath, self.__config, repotype)
            m.push()

    '''Retrieves only the metadata related to a ml-git repository'''

    def update(self):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)
        m = Metadata("", metadatapath, self.__config)
        m.update()

    '''Retrieve only the data related to a specific ML entity version'''

    def _fetch(self, tag, samples, retries=2):
        repotype = self.__repotype
        objectspath = objects_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)

        # check if no data left untracked/uncommitted. othrewise, stop.
        local_rep = LocalRepository(self.__config, objectspath, repotype)

        return local_rep.fetch(metadatapath, tag, samples, retries)

    def fetch_tag(self, tag, samples, retries=2):
        repotype = self.__repotype
        objectspath = objects_path(self.__config, repotype)

        self._checkout(tag)

        fetch_success = self._fetch(tag, samples, retries)

        if not fetch_success:
            objs = Objects("", objectspath)
            objs.fsck(remove_corrupted=True)
            self._checkout("master")
            return

        # restore to master/head
        self._checkout("master")


    def _checkout(self, tag):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)

        # checkout
        m = Metadata("", metadatapath, self.__config, repotype)
        m.checkout(tag)

    '''performs fsck on several aspects of ml-git filesystem.
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
        objectspath = objects_path(self.__config, repotype)
        indexpath = index_path(self.__config, repotype)

        o = Objects("", objectspath)
        corrupted_files_obj = o.fsck()
        corrupted_files_obj_len = len(corrupted_files_obj)

        idx = MultihashIndex("", indexpath)
        corrupted_files_idx = idx.fsck()
        corrupted_files_idx_len = len(corrupted_files_idx)

        print("[%d] corrupted file(s) in Local Repository: %s" % (corrupted_files_obj_len, corrupted_files_obj))
        print("[%d] corrupted file(s) in Index: %s" % (corrupted_files_idx_len, corrupted_files_idx))
        print("Total of corrupted files: %d" % (corrupted_files_obj_len + corrupted_files_idx_len))

    def show(self, spec):
        repotype = self.__repotype
        metadatapath = metadata_path(self.__config, repotype)
        refspath = refs_path(self.__config, repotype)

        r = Refs(refspath, spec, repotype)
        tag, sha = r.head()
        if tag is None:
            log.info("No HEAD for [%s]" % spec, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return

        self._checkout(tag)

        m = Metadata("", metadatapath, self.__config, repotype)
        m.show(spec)

        self._checkout("master")

    def _tag_exists(self, tag):
        md = MetadataManager(self.__config, self.__repotype)

        # check if tag already exists in the ml-git repository
        tags = md._tag_exists(tag)
        if len(tags) == 0:
            log.error("Tag [%s] does not exist in this repository" % tag, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def get(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False):
        metadatapath = metadata_path(self.__config)
        dt_tag, lb_tag = self._get(tag, samples, retries, force_get, dataset, labels)
        if dt_tag is not None:
            try:
                self.__repotype = "dataset"
                m = Metadata("", metadatapath, self.__config, self.__repotype)
                log.info("Initializing related dataset download")
                m.init()
                self._get(dt_tag, samples, retries, force_get, False, False)
            except Exception as e:
                log.error("LocalRepository: [%s]" % e)
        if lb_tag is not None:
            try:
                self.__repotype = "labels"
                m = Metadata("", metadatapath, self.__config, self.__repotype)
                log.info("Initializing related labels download")
                m.init()
                self._get(lb_tag, samples, retries, force_get, False, False)
            except Exception as e:
                log.error("LocalRepository: [%s]" % e)

    '''Download data from a specific ML entity version into the workspace'''

    def _get(self, tag, samples, retries=2, force_get=False, dataset=False, labels=False):
        repotype = self.__repotype
        cachepath = cache_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)
        objectspath = objects_path(self.__config, repotype)
        refspath = refs_path(self.__config, repotype)
        dataset_tag = None
        labels_tag = None
        # find out actual workspace path to save data
        categories_path, specname, _ = spec_parse(tag)

        wspath = os.path.join(get_root_path(), os.sep.join([repotype, categories_path]))

        ensure_path_exists(wspath)

        try:
            if not self._tag_exists(tag):
                return None, None
        except Exception as e:
            log.error("Invalid ml-git repository!", class_name=REPOSITORY_CLASS_NAME)
            return None, None
        curtag, _ = self._branch(specname)
        if curtag == tag:
            log.info("Already at tag [%s]" % tag, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        # check if no data left untracked/uncommitted. otherwise, stop.
        if not force_get and self._exist_local_changes(specname) is True:
            return None, None

        self._checkout(tag)

        try:
            specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
            spec = yaml_load(specpath)
            if dataset is True:
                dataset_tag = spec[repotype]['dataset']['tag']
        except Exception:
            log.warn("Repository: the dataset does not exist for related download.")
        try:
            if labels is True:
                labels_tag = spec[repotype]['labels']['tag']
        except Exception:
            log.warn("Repository: the labels does not exist for related download.")

        fetch_success = self._fetch(tag, samples, retries)

        if not fetch_success:
            objs = Objects("", objectspath)
            objs.fsck(remove_corrupted=True)
            self._checkout("master")
            return None, None

        spec_index_path = os.path.join(index_metadata_path(self.__config, repotype), specname)
        if os.path.exists(spec_index_path):
            if os.path.exists(os.path.join(spec_index_path, specname + ".spec")):
                os.unlink(os.path.join(spec_index_path, specname + ".spec"))
            if os.path.exists(os.path.join(spec_index_path, "README.md")):
                os.unlink(os.path.join(spec_index_path, "README.md"))

        try:
            r = LocalRepository(self.__config, objectspath, repotype)
            r.get(cachepath, metadatapath, objectspath, wspath, tag, samples)
        except OSError as e:
            self._checkout("master")
            if e.errno == errno.ENOSPC:
                log.error("There is not enough space in the disk. Remove some files and try again.", class_name=REPOSITORY_CLASS_NAME)
            else:
                log.error("An error occurred while creating the files into workspace: %s \n." % e, class_name=REPOSITORY_CLASS_NAME)
            return None, None
        except Exception as e:
            self._checkout("master")
            log.error("An error occurred while creating the files into workspace: %s \n." % e, class_name=REPOSITORY_CLASS_NAME)
            return None, None

        m = Metadata("", metadatapath, self.__config, repotype)
        sha = m.sha_from_tag(tag)

        r = Refs(refspath, specname, repotype)
        r.update_head(tag, sha)

        # restore to master/head
        self._checkout("master")
        return dataset_tag, labels_tag

    def _exist_local_changes(self, specname):
        new_files, deleted_files, untracked_files = self._status(specname, log_errors=False)
        if new_files is not None and deleted_files is not None and untracked_files is not None:
            unsaved_files = new_files + deleted_files + untracked_files
            if specname + ".spec" in unsaved_files:
                unsaved_files.remove(specname + ".spec")
            if "README.md" in unsaved_files:
                unsaved_files.remove("README.md")

            if len(unsaved_files) > 0:
                log.error("Your local changes to the following files would be discarded: ", class_name=REPOSITORY_CLASS_NAME)
                for file in unsaved_files:
                    print("\t%s" % file)
                log.info("Please, commit your changes before the get. You can also use the --force "
                         "option to discard these changes. See 'ml-git --help'.", class_name=REPOSITORY_CLASS_NAME)
                return True
        return False
    @staticmethod
    def _get_path_with_categories(tag):
        result = ''
        if tag:
            temp = tag.split("__")
            result = '/'.join(temp[0:len(temp)-2])

        return result

    def _status(self, spec, log_errors=True):
        repotype = self.__repotype
        indexpath = index_path(self.__config, repotype)
        metadatapath = metadata_path(self.__config, repotype)

        # All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
        idx = MultihashIndex(spec, indexpath)
        tag, sha = self._branch(spec)
        categories_path = self._get_path_with_categories(tag)

        path, file = None, None
        try:
            path, file = search_spec_file(self.__repotype, spec, categories_path)
        except Exception as e:
            if log_errors:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if path is None:
            return None, None, None

        manifest_files = ""
        if tag is not None:
            self._checkout(tag)
            m = Metadata(spec, metadatapath, self.__config, repotype)
            md_metadatapath = m.get_metadata_path(tag)
            manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
            manifest_files = yaml_load(manifest)
            self._checkout("master")
        objfiles = idx.get_index()

        new_files = []
        deleted_files = []
        untracked_files = []
        all_files = []
        for key in objfiles:
            files = objfiles[key]
            for file in files:
                if not os.path.exists(os.path.join(path, file)):
                    deleted_files.append(file)
                else:
                    new_files.append(file)
                all_files.append(file)

        if path is not None:
            for k in manifest_files:
                for file in manifest_files[k]:
                    if not os.path.exists(os.path.join(path, file)):
                        deleted_files.append(file)
                    all_files.append(file)
            for root, dirs, files in os.walk(path):
                basepath = root[len(path) + 1:]
                for file in files:
                    fullpath = os.path.join(root, file)
                    st = os.stat(fullpath)
                    if st.st_nlink <= 1:
                        untracked_files.append((os.path.join(basepath, file)))
                    elif (os.path.join(basepath, file)) not in all_files and not ("README.md" in file or ".spec" in file):
                        untracked_files.append((os.path.join(basepath, file)))
        return new_files, deleted_files, untracked_files

if __name__ == "__main__":
    from mlgit.config import config_load

    config = config_load()
    r = Repository(config)
    r.init()
    r.add("dataset-ex")
    r.commit("dataset-ex")
    r.status("dataset-ex")
