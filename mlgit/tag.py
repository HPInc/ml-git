"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""


class Tag(object):
	def __init__(self, tag):
		self._tag = tag

	'''format is <categories>+__<ml-entity-name>__<version>'''
	def parse(self, tag):
		pass

	def __repr__(self):
		return self._tag


class UsrTag(object):
	def __init__(self, tag, usrtag):
		self._tag = '._.'.join( ['_._user', tag, usrtag] )

	def _get(self):
		return self._tag

	def __repr__(self):
		return self._tag.split('._.')[2]
