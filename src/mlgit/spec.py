"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os
from mlgit.utils import get_root_path


def search_spec_file(repotype, spec):
	try:
		dir = os.path.join(get_root_path(), os.sep.join([repotype, spec]))
		files = os.listdir(dir)
	except Exception as e:  # TODO: search "." path as well
		dir = spec
		try:
			files = os.listdir(spec)
		except:
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
