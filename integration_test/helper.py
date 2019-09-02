"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import errno
import os
import os.path
import shutil
import stat
import subprocess

PATH_TEST = os.path.join(os.getcwd(),".test_env")

ML_GIT_DIR = os.path.join(PATH_TEST, ".ml-git")

GIT_PATH = os.path.join(PATH_TEST, "local_git_server.git")

GIT_WRONG_REP = 'https://wrong_repository/wrong_repository.git'

BUCKET_NAME = "mlgit"

PROFILE = "default"

def clear(path):
    # SET the permission for files inside the .git directory to clean up
    if not os.path.exists(path):
        return

    for root, _, files in os.walk(path):
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    try:
        shutil.rmtree(path)
    except Exception as e:
        print("except: ", e)


def check_output(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    error_received = err.decode("utf-8")
    process.terminate()
    return error_received