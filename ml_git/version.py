"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os


def get_version():
    version_info = read_info_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'version.info')))
    __version__ = '{}.{}.{}'.format(version_info['MAJOR_VERSION'], version_info['MINOR_VERSION'], version_info['PATCH_VERSION'])

    build_number_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'build', 'version.info'))
    if os.path.exists(build_number_file_path):
        build_number_info = read_info_file(build_number_file_path)
        __version__ += '-' + build_number_info['BUILD_NUMBER']

    return __version__


def read_info_file(file_path):
    file = open(file_path, encoding='utf-8')
    line = file.readline().strip()
    dict_info = {}
    while line:
        line_info = line.split('=')
        dict_info[line_info[0]] = line_info[1]
        line = file.readline().strip()
    file.close()
    return dict_info
