"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

messages = [
    'INFO - Admin: Initialized empty ml-git repository in',  # 0
    'INFO - Admin: You already are in a ml-git repository',  # 1
    'INFO - Admin: Add remote repository [%s] for [%s]',  # 2
    'INFO - Admin: Add remote repository [%s] for [labels]',  # 3
    'INFO - Admin: Add remote repository [%s] for [model]',  # 4
    'INFO - Admin: Changing remote from [%s]  to [%s] for  [dataset]',  # 5
    'ERROR - Admin: You are not in an initialized ml-git repository.',  # 6
    'INFO - Admin: Add store [%s://%s] with creds from profile [%s]',  # 7
    'INFO - Metadata Manager: Metadata init [%s] @ [%s]',  # 8
    'ERROR - Repository: The path [%s] already exists and is not an empty directory.',  # 9
    'ERROR - Repository: Unable to find %s. Check the remote repository used.',  # 10
    'ERROR - Repository: Unable to find remote repository. Add the remote first.',  # 11
    'INFO - Admin: Add remote repository [%s] for [model]',  # 12
    'INFO - Repository: %s adding path',  # 13
    'INFO - Repository: model adding path',  # 14
    'INFO - Repository: labels adding path',  # 15
    'ERROR - Repository: The entity name passed is wrong. Please check again',  # 16
    'INFO - Metadata Manager: Commit repo[%s] --- file[%s]',  # 17
    'INFO - Local Repository: No blobs to push at this time.',  # 18
    'INFO - Repository: dataset adding path [%s] to ml-git index',  # 19
    'INFO - Metadata Manager: Pull [%s]',  # 20
    'ERROR - Local Repository: The amount parameter should be smaller than the group size.',  # 21
    'ERROR - Local Repository: The group size parameter should be smaller than the file list size.',  # 22
    'ERROR - Local Repository: The start parameter should be smaller than the stop.',  # 23
    'ERROR - Local Repository: The stop parameter should be smaller than or equal to the file list size.',  # 24
    'ERROR - Local Repository: The start parameter should be greater than or equal to zero.',  # 25
    'ERROR - Local Repository: The step parameter should be smaller than the stop.',  # 26
    'INFO - Repository: There is no new data to add',  # 27
    'ERROR - Local Repository: The group size parameter should be greater than zero.',  # 28
    'ERROR - Local Repository: The frequency  parameter should be greater than zero.',  # 29
    'ERROR - Local Repository: The amount parameter should be smaller than the frequency.',  # 30
    'ERROR - Local Repository: The frequency  parameter should be smaller than the file list size.',  # 31
    'ERROR - Local Repository: Requires positive integer values.',  # 32
    'ERROR - Admin: Permission denied. You need write permission to initialize ml-git in this directory.',  # 33
    'ERROR - Repository: You are not in an initialized ml-git repository.',  # 34
    'INFO - MLGit: remote-fsck -- fixed   : ipld[%d] / blob[%d]',  # 35
    'Total of corrupted files: %d',  # 36
    'INFO - Metadata Manager: Pull [%s]',  # 37
    'Project Created.',  # 38
    'Successfully loaded configuration files!',  # 39
    'ERROR - Local Repository: The --random-sample=<amount:frequency> --seed=<seed>: requires positive integer values.',  # 40
    'ERROR - Local Repository: The --group-sample=<amount:group-size> --seed=<seed>: requires positive integer values.',  # 41
    'ERROR - Local Repository: The --range-sample=<start:stop:step> or  --range-sample=<start:stop>: requires positive integer values.',  # 42
    'ERROR - Local Repository: The amount parameter should be greater than zero.',  # 43
    ' Could not read from remote repository.',  # 44
    'The path [%s] is not an empty directory. Consider using --folder to create an empty folder.',  # 45
    'ERROR - Admin: Permission denied in folder',  # 46
    '2.00/2.00',  # 47
    'ERROR - Repository: No current tag for [%s]. commit first.',  # 48
    'tag \'%s\' already exists',  # 49
    'ERROR - Local Repository: Fatal downloading error [Unable to locate credentials]',  # 50
    'ERROR - Local Repository: Fatal downloading error [An error occurred (403) '
    'when calling the HeadObject operation: Forbidden',  # 51
    'ERROR - Store Factory: The config profile (%s) could not be found',  # 52
    'INFO - Repository: Create Tag Successfull',  # 53
    'The AWS Access Key Id you provided does not exist in our records.',  # 54
    'No current tag for [%s]. commit first',  # 55
    'ML %s\n|-- computer-vision\n|   |-- images\n|   |   |-- %s-ex\n',  # 56
    '-- %s : %s-ex --\ncategories:\n- computer-vision\n- images\nmanifest:\n  amount: 5\n  '
    'files: MANIFEST.yaml\n  size: 14 KB\n  store: s3h://mlgit\nname: %s-ex\nversion: %s\n\n',  # 57
    '%d missing descriptor files. Consider using the --thorough option.',  # 58
    '%d missing descriptor files. Download:',  # 59
    'Corruption detected for chunk [%s]',  # 60
    'You cannot use this command for this entity because mutability cannot be strict.',  # 61
    'The permissions for %s have been changed.',  # 62
    'File %s not found',  # 63
    'ERROR - Repository: Spec mutability cannot be changed.',  # 64
    'INFO - Repository: The spec does not have the \'mutability\' property set. Default: strict.',  # 65
    'Exporting tag [%s] from [%s] to [%s]',  # 66
    'The following files cannot be added because they are corrupted:',  # 67
    'Checkout in bare mode done.',  # 68
    'The file %s already exists in the repository. If you commit, the file will be overwritten.',  # 69
    'does not exist',  # 70
    'You cannot use this command for this entity because mutability cannot be strict.',  # 71
    'The permissions for %s have been changed.',  # 72
    'File %s not found',  # 73
    'ERROR - Repository: Spec mutability cannot be changed.',  # 74
    'INFO - Repository: The spec does not have the \'mutability\' property set. Default: strict.',  # 75
    'INFO - Admin: Removed store [s3h://%s] from configuration file.',  # 76
    'Tag: %s',  # 77
    'Message: %s',  # 78
    'Total of files: %d',  # 79
    'Workspace size: %s',  # 80
    'Added files [%s]',  # 81
    'Deleted files [%s]',  # 82
    'Files size: %s',  # 83
    'Amount of files: %s',  # 84
    'The %s doesn\'t have been initialized.',  # 85
    'You don\'t have any entity being managed.',  # 86
    'INFO - Admin: Add store [%s://%s]',  # 87
    'An entity with that name already exists.',  # 88
    'The argument `import` is mutually exclusive with argument',  # 89
    'The argument `credentials_path` is required if `import-url` is used.',  # 90
    'Invalid url: [%s]',  # 91
    'Unzipping files',  # 92
    'Error: no such option: --sample-type',  # 93
    'Could not initialize metadata for %s.',  # 94
    'Error: Invalid value for "--version-number": %s',  # 95
]
