"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os


def search_spec_file(repotype, spec, categories_path):
	dir = os.sep.join([repotype, spec])
	if not len(categories_path) > 0:
		try:
			files = os.listdir(dir)
		except Exception as e:  # TODO: search "." path as well
			files = os.listdir(spec)
	else:
		dir = os.sep.join([repotype, categories_path, spec])
		try:
			files = os.listdir(os.sep.join([repotype, categories_path, spec]))
		except Exception as e:
			return None, None

	for file in files:
		if spec in file:
			log.debug("search spec file: found [%s]-[%s]" % (dir, file))
			return dir, file

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
