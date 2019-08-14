"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.admin import remote_add
from mlgit.utils import ensure_path_exists, yaml_save, yaml_load
from mlgit.config import metadata_path
from mlgit import log
from git import Repo, Git,InvalidGitRepositoryError,GitError
import os
import yaml
from mlgit.utils import get_root_path


class MetadataRepo(object):
	def __init__(self, git, path):
		self.__path = os.path.join(get_root_path(), path)
		self.__git = git
		ensure_path_exists(self.__path)

	def init(self):
		log.info("metadata init: [%s] @ [%s]" % (self.__git, self.__path))
		try:
			Repo.clone_from(self.__git, self.__path)
		except GitError:
			raise GitError("The path [%s] already exists and is not an empty directory." % self.__path)

	def remote_set_url(self, repotype, mlgit_remote):
		try:
			remote_add(repotype, mlgit_remote)
			if(self.check_exists()):
				re = Repo(self.__path)
				re.remote().set_url(new_url=mlgit_remote)
		except InvalidGitRepositoryError:
			pass

	def check_exists(self):
		log.debug("metadata check existence [%s] @ [%s]" % (self.__git, self.__path))
		try:
			r = Repo(self.__path)
		except:
			return False
		return True

	def checkout(self, sha):
		r = Git(self.__path)
		r.checkout(sha)

	def update(self):
		log.info("Metadata Manager pull [%s]" % (self.__path))
		r = Repo(self.__path)
		o = r.remotes.origin
		r = o.pull()

	def commit(self, file, msg):
		log.info("commit : repo[%s] --- file[%s]" % (self.__path, file))
		r = Repo(self.__path)
		r.index.add([file])
		return r.index.commit(msg)

	def tag_add(self, tag):
		r = Repo(self.__path)
		return r.create_tag(tag, message='Automatic tag "{0}"'.format(tag))

	def push(self):
		log.debug("Metadata Manager: push [%s]" % (self.__path))
		r = Repo(self.__path)
		r.remotes.origin.push(tags=True)
		r.remotes.origin.push()

	def list_tags(self, spec):
		tags = []
		r = Repo(self.__path)
		for tag in r.tags:
			stag = str(tag)
			if spec in stag:
				tags.append(stag)
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
		tags= []
		r = Repo(self.__path)
		if tag in r.tags:
			tags.append(tag)

		model_tag = "__".join( tag.split("__")[-3:] )
		for rtag in r.tags:
			if model_tag in str(rtag):
				tags.append(str(rtag))

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

		print("specs: %s" % (specs))
		for specpath in specs:
			self.metadata_print(specpath, spec)

	def get(self, categories, model_name, file=None):
		if file is None:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, model_name)
		else:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, file)
		log.info("metadata GET: %s" % (full_path))
		if os.path.exists(full_path):
			return yaml_load(full_path)
		return None

	def __get_categories_spec_from_tag(tag):
		sp = tag.split("__")
		return sp[:-2], sp[-2:-1][0]


class MetadataManager(MetadataRepo):
	def __init__(self, config, type="model"):
		store = type
		#log.info("metadatamanager: %s" % (config))
		self.path = metadata_path(config, type)
		self.git =  config[type]["git"]
		# self.data = config[type]["data"]

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

if __name__=="__main__":
	r = MetadataRepo("ssh://git@github.com/standel/ml-datasets", "ml-git/datasets/")
	# tag = "vision-computing__images__cifar-10__1"
	# sha = "0e4649ad0b5fa48875cdfc2ea43366dc06b3584e"
	# #r.checkout(sha)
	# #r.checkout("master")

