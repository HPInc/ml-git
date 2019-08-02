"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os
from mlgit.utils import get_root_path


def search_spec_file(repotype, spec, categories_path):

	dir_with_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, categories_path, spec]))
	dir_without_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, spec]))
	files_with_cat_path = ''
	files_without_cat_path = ''

	try:
		files_with_cat_path = os.listdir(dir_with_cat_path)
	except Exception as e:
		try:
			files_without_cat_path = os.listdir(dir_without_cat_path)
		except Exception as e:  # TODO: search "." path as well
			return None, None

	if len(files_with_cat_path) > 0:
		for file in files_with_cat_path:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir_with_cat_path, file))
				return dir_with_cat_path, file
	else:
		for file in files_without_cat_path:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir_without_cat_path, file))
				return dir_without_cat_path, file
	return None, None


def spec_parse(spec):
	sep = "__"
	specs = spec.split('__')
	if len(specs) <= 1:
		return None, spec, None
	else:
		categories_path = os.sep.join(specs[:-1])
		specname = specs[-2]
		version = specs[-1]
		return categories_path, specname, version
