"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

messages = [
    "INFO - Admin: Initialized empty ml-git repository in",  # 0
    "INFO - Admin: You already are in a ml-git repository",  # 1
    "INFO - Admin: Add remote repository [%s] for [dataset]",  # 2
    "INFO - Admin: Add remote repository [%s] for [labels]",  # 3
    "INFO - Admin: Add remote repository [%s] for [model]",  # 4
    "INFO - Admin: Changing remote from [%s]  to [%s] for  [dataset]",  # 5
    "ERROR - Admin: You are not in an initialized ml-git repository.",  # 6
    "INFO - Admin: Add store [s3h://%s] in region [us-east-1] with creds from profile [%s]",  # 7
    "INFO - Metadata Manager: Metadata init [%s] @ [%s]",  # 8
    "ERROR - MLGit: The path [%s] already exists and is not an empty directory.",  # 9
    "ERROR - Unable to find %s. Check the remote repository used.",  # 10
    "ERROR - Unable to find remote repository. Add the remote first.",  # 11
    "INFO - Admin: Add remote repository [%s] for [model]",  # 12
    "INFO - Repository: dataset adding path",  # 13
]
