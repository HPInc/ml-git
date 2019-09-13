"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import re

from mlgit.admin import remote_add
from mlgit.manifest import Manifest
from mlgit.utils import ensure_path_exists, yaml_save, yaml_load
from mlgit.config import metadata_path
from mlgit import log
from git import Repo, Git, InvalidGitRepositoryError,GitError
import os
import yaml
from mlgit.utils import get_root_path
from mlgit.constants import METADATA_MANAGER_CLASS_NAME, HEAD_1


class MetadataRepo(object):
	def __init__(self, git, path):
		try:
			self.__path = os.path.join(get_root_path(), path)
			self.__git = git
			ensure_path_exists(self.__path)
		except Exception as e:
			if str(e) == "'Metadata' object has no attribute '_MetadataRepo__git'":
				log.error('You are not in an initialized ml-git repository.', class_name=METADATA_MANAGER_CLASS_NAME)
			return

	def init(self):
		log.info("Metadata init [%s] @ [%s]" % (self.__git, self.__path), class_name=METADATA_MANAGER_CLASS_NAME)
		try:
			Repo.clone_from(self.__git, self.__path)
		except GitError as g:
			if "fatal: repository '' does not exist" in g.stderr:
				log.error('Unable to find remote repository. Add the remote first.', class_name=METADATA_MANAGER_CLASS_NAME)
			if 'Repository not found' in g.stderr:
				log.error('Unable to find '+self.__git+'. Check the remote repository used.', class_name=METADATA_MANAGER_CLASS_NAME)
			if 'already exists and is not an empty directory' in g.stderr:
				log.error("The path [%s] already exists and is not an empty directory." % self.__path, class_name=METADATA_MANAGER_CLASS_NAME)
			if 'Authentication failed' in g.stderr:
				log.error("Authentication failed for git remote", class_name=METADATA_MANAGER_CLASS_NAME)
			return

	def remote_set_url(self, repotype, mlgit_remote):
		try:
			if self.check_exists():
				re = Repo(self.__path)
				re.remote().set_url(new_url=mlgit_remote)
		except InvalidGitRepositoryError as e:
			raise e

	def check_exists(self):
		log.debug("Metadata check existence [%s] @ [%s]" % (self.__git, self.__path), class_name=METADATA_MANAGER_CLASS_NAME)
		try:
			r = Repo(self.__path)
		except:
			return False
		return True

	def checkout(self, sha):
		r = Git(self.__path)
		r.checkout(sha)

	def update(self):
		log.info("Pull [%s]" % self.__path, class_name=METADATA_MANAGER_CLASS_NAME)
		r = Repo(self.__path)
		o = r.remotes.origin
		r = o.pull()

	def commit(self, file, msg):
		log.info("Commit repo[%s] --- file[%s]" % (self.__path, file), class_name=METADATA_MANAGER_CLASS_NAME)
		r = Repo(self.__path)
		r.index.add([file])
		return r.index.commit(msg)

	def tag_add(self, tag):
		r = Repo(self.__path)
		return r.create_tag(tag, message='Automatic tag "{0}"'.format(tag))

	def push(self):
		log.debug("Push [%s]" % self.__path, class_name=METADATA_MANAGER_CLASS_NAME)
		r = Repo(self.__path)
		r.remotes.origin.push(tags=True)
		r.remotes.origin.push()

	def fetch(self):
		try:
			log.debug("Metadata Manager: fetch [%s]" % self.__path)
			r = Repo(self.__path)
			r.remotes.origin.fetch()
		except GitError as e:
			err = e.stderr
			match = re.search("stderr: 'fatal:(.*)'$", err)
			if match:
				err = match.group(1)
				log.error("Metadata Manager: %s " % err)
			else:
				log.error("Metadata Manager: %s " % err)
			return False

	def list_tags(self, spec):
		tags = []
		try:
			r = Repo(self.__path)
			for tag in r.tags:
				stag = str(tag)
				if spec in stag:
					tags.append(stag)
		except Exception as e:
			log.error("Invalid ml-git repository!", class_name=METADATA_MANAGER_CLASS_NAME)
		return tags

	def delete_tag(self, tag):
		pass

	def _usrtag_exists(self, usrtag):
		r = Repo(self.__path)
		sutag = usrtag._get()
		for tag in r.tags:
			stag = str(tag)
			if sutag in stag:
				return True
		return False

	def _tag_exists(self, tag):
		tags = []
		r = Repo(self.__path)
		if tag in r.tags:
			tags.append(tag)

		model_tag = "__".join(tag.split("__")[-3:])
		for r_tag in r.tags:
			if model_tag in str(r_tag):
				tags.append(str(r_tag))

		return tags

	def __realname(self, path, root=None):
		if root is not None:
			path=os.path.join(root, path)
		result=os.path.basename(path)
		return result

	def list(self, title="ML Datasets"):
		metadata_path = self.__path

		prefix=0
		if metadata_path != '/':
			if metadata_path.endswith('/'): metadata_path=metadata_path[:-1]
			prefix=len(metadata_path)

		print(title)
		for root, dirs, files in os.walk(metadata_path):
			if root == metadata_path: continue
			if ".git" in root: continue

			level = root[prefix:].count(os.sep)
			indent=subindent =''
			if level > 0:
				indent = '|   ' * (level-1) + '|-- '
			subindent = '|   ' * (level) + '|-- '
			print('{}{}'.format(indent, self.__realname(root)))
			# print dir only if symbolic link; otherwise, will be printed as root
			for d in dirs:
				if os.path.islink(os.path.join(root, d)):
					print('{}{}'.format(subindent, self.__realname(d, root=root)))
			#for f in files:
			#	if "README" in f: continue
			#	if "MANIFEST.yaml" in root: continue # TODO : check within the ML entity metadat for manifest files
			#	print('{}{}'.format(subindent, self.__realname(f, root=root)))

	def metadata_print(self, metadata_file, spec_name):
		md = yaml_load(metadata_file)

		sections = ["dataset", "model", "labels"]
		for section in sections:
			if section in [ "model", "dataset", "labels" ]:
				try:
					md[section] # "hack" to ensure we don't print something useless
					# "dataset" not present in "model" and vice versa
					print("-- %s : %s --" % (section, spec_name))
				except:
					continue
			elif section not in [ "model", "dataset", "labels" ]:
				print("-- %s --" % (section))
			try:
				print(yaml.dump(md[section]))
			except:
				continue

	def sha_from_tag(self, tag):
		try:
			r = Repo(self.__path)
			return r.git.rev_list(tag).split("\n", 1)[0]
		except:
			return None

	def git_user_config(self):
		r = Repo(self.__path)
		reader = r.config_reader()
		config = {}
		types = ["email", "name"]
		for type in types:
			try:
				field = reader.get_value("user", type)
				config[type] = field
			except:
				config[type] = None
		return config

	def metadata_spec_from_name(self, specname):
		specs = []
		for root, dirs, files in os.walk(self.__path):
			if ".git" in root: continue
			if specname in root:
				specs.append(os.path.join(root, specname + ".spec"))
		return specs

	def show(self, spec):
		specs = self.metadata_spec_from_name(spec)

		for specpath in specs:
			self.metadata_print(specpath, spec)

	def get(self, categories, model_name, file=None):
		if file is None:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, model_name)
		else:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, file)
		log.info("Metadata GET %s" % full_path, class_name=METADATA_MANAGER_CLASS_NAME)
		if os.path.exists(full_path):
			return yaml_load(full_path)
		return None

	def reset(self):
		r = Repo(self.__path)
		# get current tag reference
		tag = self.get_current_tag()
		# reset
		try:
			r.head.reset(HEAD_1, index=True, working_tree=True, paths=None)
		except GitError as g:
			if "Failed to resolve 'HEAD~1' as a valid revision." in g.stderr:
				log.error('There is no commit to go back. Do at least two commits.',
						class_name=METADATA_MANAGER_CLASS_NAME)
			raise g
		# delete the associated tag
		r.delete_tag(tag)

	def get_metadata_manifest(self):
		for root, dirs, files in os.walk(self.__path):
			for file in files:
				if 'MANIFEST.yaml' in file:
					return Manifest(os.path.join(root, file))
		return None

	def get_current_tag(self):
		repo = Repo(self.__path)
		tag = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
		return tag


class MetadataManager(MetadataRepo):
	def __init__(self, config, type="model"):
		self.path = metadata_path(config, type)
		self.git = config[type]["git"]

		super(MetadataManager, self).__init__(self.git, self.path)


class MetadataObject(object):
	def __init__(self):
		pass

# TODO signed tag
# try:
#             self.repo.create_tag(self.config['tag'],
#                 verify=True,
#                 ref=None)
#             print('okay')
#         except:
#             print('not okay')


if __name__ == "__main__":
	r = MetadataRepo("ssh://git@github.com/standel/ml-datasets", "ml-git/datasets/")
	# tag = "vision-computing__images__cifar-10__1"
	# sha = "0e4649ad0b5fa48875cdfc2ea43366dc06b3584e"
	# #r.checkout(sha)
	# #r.checkout("master")

