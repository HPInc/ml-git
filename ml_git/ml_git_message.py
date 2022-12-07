"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

doc = '''
  datasets:
    categories:
    - vision-computing
    - images
    mutability: strict
    manifest:
      files: MANIFEST.yaml
      storage: s3h://some-bucket
    name: datasets-ex
    version: 5
'''

output_messages = {
    'DEBUG_REMOVE_REMOTE': 'Removing remote from local repository [%s]',
    'DEBUG_BUILDING_STORAGE_LOG': 'Building the storage.log with these added files',
    'DEBUG_OBJECT_ALREADY_IN_STORAGE': 'Object [%s] already in %s storage',
    'DEBUG_STORAGE_AND_BUCKET': 'Storage [%s] ; bucket [%s]',
    'DEBUG_CHECKSUM_VERIFIED': 'Checksum verified for chunk [%s]',
    'DEBUG_KEY_PATH_ALREADY_EXISTS': 'Key path [%s] already exists in drive path [%s].',
    'DEBUG_CONNECT_PROFILE_AND_REGION': 'Connect - profile [%s] ; region [%s]',
    'DEBUG_CONNECTING_TO_STORAGE': 'Connecting to [%s]',
    'DEBUG_DOWNLOADING_FROM_BUCKET': 'Get - downloading [%s]  from bucket [%s] into file [%s]',
    'DEBUG_DELETING_FROM_BUCKET': 'Delete - deleting [%s] from bucket [%s]',
    'DEBUG_FILE_NOT_IN_LOCAL_REPOSITORY': 'File [%s] not present in local repository',
    'DEBUG_CONTAINER_ALREADY_EXISTS': 'Container %s already exists',
    'DEBUG_AZURE_CLI_NOT_FIND': 'Azure cli configurations not find.',
    'DEBUG_PUSH_BLOB_TO_STORAGE': 'LocalRepository: push blob [%s] to storage',
    'DEBUG_DELETE_BLOB_FROM_STORAGE': 'Delete blob [%s] from storage',
    'DEBUG_CHECK_IPLD': 'LocalRepository: check ipld [%s] in storage',
    'DEBUG_MISSING_IPLD': 'LocalRepository: missing ipld [%s] in storage',
    'DEBUG_METADATA_CHECK_EXISTENCE': 'Metadata check existence [%s] @ [%s]',
    'DEBUG_PUSH': 'Push [%s]',
    'DEBUG_FETCH': ' fetch [%s]',
    'DEBUG_METADATA_PATH': 'Metadata path [%s]',
    'DEBUG_COMMIT_MESSAGE': 'Commit message [%s]',
    'DEBUG_DATASET_PATH': 'Dataset path: %s',
    'DEBUG_COMMIT_SPEC': 'Commit spec [%s] to ml-git metadata',
    'DEBUG_NEW_TAG_CREATED': 'New tag created [%s]',
    'DEBUG_CREATE_WORKER_POOL': 'Create a worker pool with [%d] threads & retry strategy of [%d]',
    'DEBUG_WAIT_BEFORE_NEXT_ATTEMP': 'Wait [%d] before next attempt',
    'DEBUG_WORKER_SUCESS': 'Worker success at attempt [%d]',
    'DEBUG_SETTING_HEAD': 'Setting head of [%s] to [%s]-[%s]',
    'DEBUG_TAG_CHECK': 'Check if tag already exists',
    'DEBUG_MESSAGE_VALUE': '%s -> %s',
    'DEBUG_TAG_CHECK_FOR': 'Check if tag [%s] already exists',
    'DEBUG_VERSION_INCREMENTED_TO': 'Version incremented to %s.',
    'DEBUG_VERSION_CHANGED_TO': 'Version changed to %s.',
    'DEBUG_LINK_FROM_TO': 'Link from [%s] to [%s]',
    'DEBUG_UPDATE_LOG': 'Update hashfs log',
    'DEBUG_UPDATE_LOG_LIST_FILES': 'Update hashfs log with a list of files to keep',
    'DEBUG_UPDATE_LOG_KEY': 'Update log for key [%s]',
    'DEBUG_LOADING_LOG': 'Loading log file',
    'DEBUG_CHUNK_ALREADY_EXISTS': 'Chunk [%s]-[%d] already exists',
    'DEBUG_ADDING_CHUNK': 'Add chunk [%s]-[%d]',
    'DEBUG_GET_CHUNK': 'Get chunk [%s]-[%d]',
    'DEBUG_BLOB_ALREADY_COMMITED': 'Blob %s already commited',
    'DEBUG_REMOVING_FILE': 'Removing file [%s]',
    'DEBUG_ADD_FILE': 'Add file [%s] to ml-git index',
    'DEBUG_FILE_NOT_INDEX': 'The file [{}] isn\'t in index',
    'DEBUG_FILE_ALREADY_EXISTS_REPOSITORY': 'File [%s] already exists in ml-git repository',
    'DEBUG_FILE_WAS_MODIFIED': 'File [%s] was modified',
    'DEBUG_GETTING_IPLD_KEY': 'Getting ipld key [%s]',
    'DEBUG_DOWNLOADING_IPLD': 'Downloading ipld [%s]',
    'DEBUG_GETTING_BLOB': 'Getting blob [%s]',
    'DEBUG_DOWNLOADING_BLOB': 'Downloading blob [%s]',
    'DEBUG_FLAG_WAS_CREATED': 'A flag was created to save that the checkout was carried out with sample',
    'DEBUG_IPLD_NOT_PRESENT': 'LocalRepository: ipld [%s] not present for full verification',
    'DEBUG_FILE_NOT_CACHE': 'File is not in cache',
    'DEBUG_CORRUPTION_DETECTED': 'Corruption detected for chunk [%s] - got [%s]',
    'DEBUG_CORRUPTION_DETECTED_FOR': 'Corruption detected for chunk [%s]',
    'DEBUG_BLOB_ALREADY_EXISTS': 'The specified blob [%s] already exists.',
    'DEBUG_ALREADY_IN_GIT_REPOSITORY': 'There is already a git repository initialized in the project root [%s]',
    'DEBUG_BUCKET_REGION_NOT_FIND': 'Could not find bucket region entered',
    'DEBUG_RATE_LIMIT': 'Remaining {} rate limit: [{}]. It will reset after [{}s]',
    'DEBUG_EXECUTING_COMMAND': 'Executing git command: %s',
    'DEBUG_GIT_COMMAND_EXECUTION': 'Git command output: %s',
    'DEBUG_UNPUBLISHED_COMMITS': 'Could not get unpublished commits quantity. Returning default value (0) for %s. %s',
    'DEBUG_ENTITIES_RELATIONSHIP': 'Could not get the entities to list its relationships. {}.',
    'DEBUG_UNZIPPING_FILE': 'Unzipping file: {}',
    'DEBUG_RESTORED_FILE': 'The file [{}] has been restored to the original version.',
    'DEBUG_LOADING_CONFIG_FILE': 'Loading config file from {}',
    'DEBUG_LOCAL_CONFIG_FILE_NOT_EXISTS': 'Local config file does not exist',
    'DEBUG_MERGING_LOCAL_AND_GLOBAL_CONFIG': 'Merging local and global configuration files',
    'DEBUG_CLEANING_DIR': 'Cleaning temporary dir',

    'INFO_INITIALIZED_PROJECT_IN': 'Initialized empty ml-git repository in %s',
    'INFO_ADD_REMOTE': 'Add remote repository [%s] for [%s]',
    'INFO_CHECKOUT_LATEST_TAG': 'Performing checkout on the entity\'s latest tag [%s]',
    'INFO_CHECKOUT_TAG': 'Performing checkout in tag %s',
    'INFO_METADATA_INIT': 'Metadata init [%s] @ [%s]',
    'INFO_COMMIT_REPO': 'Commit repo[%s] --- file[%s]',
    'INFO_CHANGING_REMOTE': 'Changing remote from [%s] to [%s] for [%s]',
    'INFO_REMOVE_REMOTE': 'Removing remote repository [%s] from [%s].',
    'INFO_ADD_STORAGE': 'Add storage [%s://%s] with creds from profile [%s]',
    'INFO_ADD_STORAGE_WITHOUT_PROFILE': 'Add storage [%s://%s]',
    'INFO_INITIALIZING_RESET': 'Initializing reset [%s] [%s] of commit. ',
    'INFO_STARTING_GC': 'Starting the garbage collector for %s',
    'INFO_REMOVED_FILES': 'A total of %s files have been removed from %s',
    'INFO_RECLAIMED_SPACE': 'Total reclaimed space %s.',
    'INFO_ENTITY_DELETED': 'Entity %s was deleted',
    'INFO_WRONG_ENTITY_TYPE': 'Metrics cannot be added to this entity: [%s].',
    'INFO_PROJECT_UPDATE_SUCCESSFULLY': 'Project updated successfully',
    'INFO_ASSOCIATE_DATASETS': 'Associate datasets [%s]-[%s] to the %s.',
    'INFO_UPDATE_THE_PROJECT': 'It was observed that the directories of this project follow the scheme of old versions of ml-git.\n' +
                               '\tTo continue using this project it is necessary to update the directories.',
    'INFO_REMOVED_STORAGE': 'Removed storage [%s://%s] from configuration file.',

    'INFO_AKS_IF_WANT_UPDATE_PROJECT': '\tDo you want to update your project now? (Yes/No) ',
    'INFO_FILE_STORED_IN_BUCKET': 'Put - stored [%s] in bucket [%s] with key [%s]-[%s]',
    'INFO_PARANOID_MODE_ACTIVE': 'Paranoid mode is active - Downloading files: ',
    'INFO_FIXING_CORRUPTED_FILES_IN_STORAGE': 'Fixing corrupted files in remote storage',
    'INFO_EXPORTING_TAG': 'Exporting tag [%s] from [%s] to [%s].',
    'INFO_METRICS_EXPORTED': 'The metrics were exported to the file: {}',
    'INFO_ALREADY_IN_RESPOSITORY': 'You already are in a ml-git repository',
    'INFO_ADDING_PATH': '%s adding path',
    'INFO_MLGIT_PULL': 'Pull [%s]',
    'INFO_NO_NEW_DATA_TO_ADD': 'There is no new data to add',
    'INFO_REMOTE_FSCK_FIXED': 'remote-fsck -- fixed   : ipld[%d] / blob[%d]',
    'INFO_REMOTE_FSCK_FIXED_LIST': '%s fixed: %s',
    'INFO_REMOTE_FSCK_UNFIXED_LIST': '%s unfixed:',
    'INFO_DATASETS_CREATED': 'Dataset artifact created.',
    'INFO_MODELS_CREATED': 'Model artifact created.',
    'INFO_LABELS_CREATED': 'Labels artifact created.',
    'INFO_SUCCESS_LOAD_CONFIGURATION': 'Successfully loaded configuration files!',
    'INFO_NOT_READY_REMOTE_REPOSITORY': 'Could not read from remote repository.',
    'INFO_TAG_ALREDY_EXISTS': 'tag \'%s\' already exists',
    'INFO_CALLING_HEADOBJECT': 'when calling the HeadObject operation: Forbidden',
    'INFO_CREATE_TAG_SUCCESS': 'Create Tag Successfull',
    'INFO_MISSING_DESCRIPTOR_FILES': '%d missing descriptor files. Consider using the --thorough option.',
    'INFO_MISSING_DESCRIPTOR_FILES_DOWNLOAD': '{} missing descriptor files detected. Download:',
    'INFO_CHECKOUT_BARE_MODE': 'Checkout in bare mode done.',
    'INFO_MUTABILITY_CANNOT_BE_STRICT': 'You cannot use this command for this entity because mutability cannot be strict.',
    'INFO_PERMISSIONS_CHANGED_FOR': 'The permissions for %s have been changed.',
    'INFO_TAG': 'Tag: %s',
    'INFO_MESSAGE': 'Message: %s',
    'INFO_FILES_TOTAL': 'Total of files: %d',
    'INFO_WORKSPACE_SIZE': 'Workspace size: %s',
    'INFO_ADDED_FILES': 'Added files [%s]',
    'INFO_DELETED_FILES': 'Deleted files [%s]',
    'INFO_FILES_SIZE': 'Files size: %s',
    'INFO_AMOUNT_SIZE': 'Amount of files: %s',
    'INFO_NOT_INITIALIZED': 'The %s doesn\'t have been initialized.',
    'INFO_NONE_ENTITY_MANAGED': 'You don\'t have any entity being managed.',
    'INFO_NONE_ENTITY_FILES_MANAGED': 'You don\'t have any files being managed in this project.',
    'INFO_ENTITY_NAME_EXISTS': 'An entity with that name already exists.',
    'INFO_EXCLUSIVE_IMPORT_ARGUMENT': 'The argument `import` is mutually exclusive with argument',
    'INFO_CHECKING_FILES_TO_BE_UNZIPPED': 'Checking for files that need to be unzipped.',
    'INFO_CANNOT_ADD_NEW_DATA_AN_ENTITY': 'You cannot add new data to an entity that is based on a checkout with the --sampling option.',
    'INFO_INITIALIZING_PROJECT': 'Initializing the project with global settings',
    'INFO_ARE_NOT_IN_INITIALIZED_PROJECT': 'You are not in an initialized ml-git repository and do not have a global configuration.',
    'INFO_NOT_GIT_REPOSITORY': 'fatal: not a git repository (or any of the parent directories): .git',
    'INFO_PATHSPEC_KNOWN_GIT': 'error: pathspec \'%s\' did not match any file(s) known to git',
    'INFO_UNABLE_AZURE_CONNECTION': 'Unable to connect to the Azure storage.',
    'INFO_TAG_ALREADY_EXISTS': 'Tag [%s] already exists in the ml-git repository.',
    'INFO_CREATE_ABORTED': 'Create command aborted!',
    'INFO_NO_FILES_COMMIT_FOR': 'No files to commit for [%s]',
    'INFO_ADDING_PATH_TO': '%s adding path [%s] to ml-git index',
    'INFO_STATUS_OF': '%s: status of ml-git index for [%s]',
    'INFO_NO_HEAD_FOR': 'No HEAD for [%s]',
    'INFO_INITIALIZING_ENTITY_DOWNLOAD': 'Initializing related %s download',
    'INFO_ALREADY_TAG': 'Already at tag [%s]',
    'INFO_SPEC_NOT_HAVE_MUTABILITY': 'The spec does not have the \'mutability\' property set. Default: strict.',
    'INFO_STARTING_INTEGRITY_CHECK': 'Starting integrity check on [{}]',
    'INFO_FINISH_INTEGRITY_CHECK': 'Finished integrity check on [{}]',
    'INFO_REMOVING_CORRUPTED_FILES': 'Removing %s corrupted files',
    'INFO_GETTING_FILE': 'Getting file [%s] from local index',
    'INFO_NO_BLOBS_TO_PUSH': 'No blobs to push at this time.',
    'INFO_CORRUPTED_FILES': 'Corrupted files: %d',
    'INFO_REMOTE_FSCK_TOTAL': 'remote-fsck -- total verified : ipld[%d] / blob[%d]',
    'INFO_LISTING_BLOBS': '\nListing blobs in container:',
    'INFO_FILE_LOCATED_IN_TRASH': 'File [{}] located in trash.',
    'INFO_CREATING_GIT_REPOSITORY': 'Creating new git repository at project root [%s]',
    'INFO_CREATING_REMOTE': 'Adding remote to the initialized project [%s]',
    'INFO_PUSH_CONFIG_FILE': 'Pushing config file to remote repository',
    'INFO_CHANGE_IN_CONFIG_FILE': 'When making changes to the config file we strongly recommend that you upload these changes to '
                                  'the Git repository. For this, see: ml-git repository config push --help',
    'INFO_SAVE_RELATIONSHIP_GRAPH': 'The relationship graph was saved in: {}',
    'INFO_ENTITIES_RELATIONSHIPS_NOT_FOUND': 'No relationships were found for your project entities.',
    'INFO_TOTAL_UNZIPPED_FILES': 'Total unzipped files: {}',
    'INFO_FILE_AUTOMATICALLY_ADDED': 'File {} has been automatically added to staged files.',
    'INFO_SUMMARY_FSCK_FILES': 'Total of {} files detected: {}. {}',
    'INFO_FSCK_CORRUPTED_FILES': '\n[{}] corrupted file(s) in Local Repository {}\n[{}] corrupted file(s) in Index {}\nTotal of corrupted files detected: {}',
    'INFO_FSCK_FIXED_FILES': 'Total of fixed files (corrupted and missing): {}. {}',
    'INFO_USE_FIX_WORKSPACE': 'It has been detected that you have corrupted files in the workspace, '
                              'you can use the --fix-worskpace option to fix the identified files.',
    'INFO_FSCK_VERBOSE_MODE': 'For more information about the corrupted files you can run the command with the --full option.',
    'INFO_SEE_ALL_CORRUPTED_FILES': 'You can view the complete list of corrupted files using the status command.',
    'INFO_SEE_ALL_FILES': 'You can view the complete list of files at logs/ml-git_execution.log',
    'INFO_LIST_OF_MISSING_FILES': 'List of missing descriptor files: %s',
    'INFO_SEE_COMPLETE_LIST_OF_MISSING_FILES': 'You can use the --full option to see the complete list of missing descriptor files.',
    'INFO_WIZARD_MODE_CHANGED': 'Wizard mode changed to \'{}\'',
    'INFO_SELECT_STORAGE': 'Select the storage where this entity\'s data should be stored:',
    'INFO_CREATE_NEW_STORAGE_OPTION': '[X] - New Data Storage Configuration\n   ',
    'INFO_DEFINE_WIZARD_MESSAGE': 'Define the {}: ',
    'INFO_SELECT_STORAGE_OPTION': 'Which storage do you want to use (a number or new data storage)? ',
    'INFO_CONFIGURE_AZURE': 'Configure the azure according to the following documentation: '
                            'https://github.com/HPInc/ml-git/blob/main/docs/azure_configurations.md',
    'INFO_DEFINE_STORAGE_TYPE': 'Define the storage type',
    'INFO_STARTING_IPLDS_CHECK': 'Starting the IPLD check on storage',
    'INFO_STARTING_BLOBS_CHECK': 'Starting the blobs check on storage',
    'INFO_FSCK_COMPLETE': 'The file system consistency check is complete.',
    'INFO_FIXING_CORRUPTED_FILES': 'Fixing {} corrupted file(s) found in {} entity',
    'INFO_MISSING_BLOB_FILES_DOWNLOAD': '{} missing blob files detected. Download:',
    'INFO_FSCK_SUMMARY': 'Summary of the results found in the execution:',
    'INFO_GETTING_FILES': 'Downloading files needed to mount the desired file',
    'INFO_MOUNTING_FILE': 'Mounting file [{}] in current directory [{}].',
    'INFO_SUCCESSFULLY_MOUNTED_FILE': 'File mounted successfully.',
    'INFO_CHANGING_MUTABILITY': 'Making necessary changes to change mutability.',
    'INFO_SUCCESSFULLY_CHANGE_MUTABILITY': 'Mutability successfully changed from {} to {}.',
    'INFO_MUTABILITY_CHANGE_DETECTED': 'A mutability change between entity versions was detected. From {} to {}',

    'ERROR_PATH_NOT_EMPTY': 'The path [%s] is not an empty directory.',
    'ERROR_WITHOUT_TAG_FOR_THIS_ENTITY': 'No tags found for that entity.',
    'ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME': 'You have more than one entity with the same name. Use one of the following tags to perform the checkout:\n',
    'ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT': 'The version specified for that entity does not exist. Last entity tag:\n\t{}',
    'ERROR_UNINITIALIZED_METADATA': 'You don\'t have any metadata initialized',
    'ERROR_REMOTE_UNCONFIGURED': 'Remote URL not found for [%s]. Check your configuration file.',
    'ERROR_ENTITY_NOT_FOUND': 'Entity type [%s] not found in your configuration file.',
    'ERROR_REMOTE_NOT_FOUND': 'Remote URL not found.',
    'ERROR_MISSING_OPTION': 'Missing option "--{}".',
    'ERROR_INVALID_TYPE_OF_FILE': 'This type of file is not supported, use one of the following types: %s',
    'ERROR_SPEC_WITHOUT_MUTABILITY': 'You need to define a mutability type when creating a new entity. '
                                     'Your spec should look something like this:' + doc,
    'ERROR_AWS_KEY_NOT_EXIST': 'The AWS Access Key Id you provided does not exist in our records.',
    'ERROR_BUCKET_DOES_NOT_EXIST': 'This bucket does not exist -- [%s]',
    'ERROR_INVALID_ENTITY_TYPE': 'Invalid entity type. Valid values are: %s',
    'ERROR_INVALID_STATUS_DIRECTORY': 'The directory informed is invalid.',
    'ERROR_OBJECT_NOT_FOUND': 'Object [%s] not found',
    'ERROR_NO_SUCH_OPTION': 'no such option: %s',
    'ERROR_INVALID_VALUE_FOR': 'Error: Invalid value for \'%s\': %s',
    'ERROR_PROJECT_NEED_BE_UPDATED': 'To continue using this project it is necessary to update it.',
    'ERROR_UNKNOWN_STORAGE_TYPE': 'Unknown data storage type [%s], choose one of these %s.',
    'ERROR_DRIVE_PATH_NOT_FOUND': 'Drive path [%s] not found.',
    'ERROR_NOT_FOUND': '[%s] not found.',
    'ERROR_FILE_COULD_NOT_BE_UPLOADED': 'The file could not be uploaded: [%s]',
    'ERROR_AUTHETICATION_FAILED': 'Authentication failed',
    'ERROR_BUCKET_NOT_CONFIGURED': 'Put - bucket [%s] not configured with Versioning',
    'ERROR_AZURE_CREDENTIALS_NOT_FOUND': 'Azure credentials could not be found. See the ml-git documentation for how to configure.',
    'ERROR_WITHOUT_STORAGE': 'No storage for [%s]',
    'ERROR_CONFIG_PROFILE_NOT_FOUND': 'The config profile (%s) could not be found',
    'ERROR_BLOB_NOT_FOUND_EXITING': 'Blob [%s] not found. exiting...',
    'ERROR_ADDING_INTO_CACHE': '\n Error adding into cache dir [%s] -- [%s]',
    'ERROR_INVALID_REPOSITORY': 'Invalid ml-git repository!',
    'ERROR_NO_COMMIT_TO_BACK': 'There is no commit to go back. Do at least two commits.',
    'ERROR_IN_INTIALIZED_PROJECT': 'You are in initialized ml-git project.',
    'ERROR_MINIMAL_CONFIGURATION': 'Wrong minimal configuration files!',
    'ERROR_NECESSARY_ATTRIBUTE': 'It is necessary to pass the attribute \'seed\' in \'sampling\'. Example: {\'group\': \'1:2\', \'seed\': \'10\'}.',
    'ERROR_SAMPLING_OPTION': 'To use the sampling option, you must pass a valid type of sampling (group, random or range).',
    'ERROR_INVALID_ENTERED_ENTITY_TYPE': 'The type of entity entered is invalid. Valid types are: [repository, dataset, labels or model]',
    'ERROR_METADATA_MESSAGE': '\t%s',
    'ERROR_NO_MANIFEST_FILE_FOUND': 'No manifest file found in [%s]',
    'ERROR_COULD_NOT_FIND_FILE': 'Could not find file {}. Entity repository must have {} file',
    'ERROR_ENTITY_NEEDS_CATATEGORY': 'You must place at least one category in the entity .spec file',
    'ERROR_INVALID_DATASET_SPEC': 'Error: invalid dataset spec (Missing name). It should look something like this:\n%s',
    'ERROR_REPOSITORY_NOT_FOUND': 'No repositories found, verify your configurations!',
    'ERROR_WORKER_FAILURE': 'Worker failure - [%s] -- [%d] attempts',
    'ERROR_INVALID_YAML_CONFIG': '.ml-git/config.yaml invalid. It should look something like this:\n%s',
    'ERROR_NOT_INITIALIZED': 'The %s has not been initialized',
    'ERROR_TAG_ALREADY_EXISTS': 'Tag [%s] already exists.',
    'ERROR_NAME_EMAIL_CONFIGURATION': 'Your name and email address need to be configured in git. Please see the commands below:',
    'ERROR_USERNAME_CONFIG': 'git config --global user.name \'Your Name\'',
    'ERROR_USEREMAIL_CONFIG': 'git config --global user.email you@example.com',
    'ERROR_METADATA_COULD_NOT_UPDATED': 'Could not update metadata. Check your remote configuration. {}',
    'ERROR_TAG_NOT_EXISTS_REPOSITORY': 'Tag [%s] does not exist in this repository',
    'ERROR_LOCALREPOSITORY_MESSAGE': 'LocalRepository: [%s]',
    'ERROR_UNABLE_CHECKOUT': 'Unable to checkout to {}',
    'ERROR_NOT_DISK_SPACE': 'There is not enough space in the disk. Remove some files and try again.',
    'ERROR_WHILE_CREATING_FILES': 'An error occurred while creating the files into workspace: %s \n.',
    'ERROR_INVALID_MUTABILITY_TYPE': 'Invalid mutability type.',
    'ERROR_CHUNK_WRONG_DIRECTORY': 'Chunk found in wrong directory. Expected [%s]. Found [%s]',
    'ERROR_INVALID_VERSION_INCREMENT': 'Invalid version, could not increment.  File:\n     %s',
    'ERROR_INVALID_VERSION_GET': 'Invalid version, could not get.  File:\n     %s',
    'ERROR_NO_NAME_PROVIDED': 'No %s name provided, can\'t increment version.',
    'ERROR_INVALID_BUCKET_NAME': 'Invalid bucket name in spec file.\n',
    'ERROR_ADDING_DIR': 'Error adding dir [%s] -- [%s]',
    'ERROR_FATAL_PUSH': 'LocalRepository: fatal push error [%s]',
    'ERROR_FATAL_FETCH': 'LocalRepository: fatal fetch error [%s]',
    'ERROR_FATAL_DELETE': 'Fatal delete error [%s]',
    'ERROR_CANNOT_DELETE_ALL_FILES': 'It was not possible to delete all files',
    'ERROR_NO_SPEC_FILE_FOUND': 'No spec file found. You need to initialize an entity (dataset|model|label) first',
    'ERROR_ADDING_INTO_WORKSPACE': 'Error adding into workspace dir [%s] -- [%s]',
    'ERROR_TO_FETCH_FILE': 'Error to fetch file -- [%s]',
    'ERROR_TO_FSCK_IPLD': 'LocalRepository: Error to fsck ipld -- [%s]',
    'ERROR_FSCK_BLOB': 'LocalRepository: Error to fsck blob -- [%s]',
    'ERROR_REMOTE_FSCK_UNFIXED': 'remote-fsck -- unfixed : ipld[%d] / blob[%d]',
    'ERROR_DISCARDED_LOCAL_CHANGES': 'Your local changes to the following files would be discarded: ',
    'ERROR_FATAL_DOWNLOADING': 'Fatal downloading error [%s]',
    'ERROR_EXPORT_FILES': 'Error to export files -- [%s]',
    'ERROR_PUSH_METADATA': 'Error on push metadata to git repository. Please update your ml-git project!',
    'ERROR_NO_ENTITY_LOG': 'No log found for entity [%s]',
    'ERROR_INVALID_BATCH_SIZE': 'The batch size value is invalid in the config file for the [%s] key',
    'ERROR_INVALID_STORAGE_TYPE': 'Invalid storage type.',
    'ERROR_INVALID_VALUE_IN_CONFIG': 'Invalid value in config file for the [%s] key. This is should be a integer number greater than 0.',
    'ERROR_DOWNLOADING_IPLD': 'Error download ipld [%s]',
    'ERROR_DOWNLOAD_BLOG': 'error download blob [%s]',
    'ERROR_PATH_NOT_FOUND': 'Path %s not found',
    'ERROR_BUCKET_NOT_FOUND': 'Bucket [%s] not found.',
    'ERROR_BUCKET_ENDPOINT_CONNECTION': 'There was an error checking if bucket \'{}\' exists. ERROR: {}. \n  '
                                        'Please check if the storage service is up and running.',
    'ERROR_INVALID_URL': 'Invalid url: [%s]',
    'ERROR_INVALID_IPLD': 'Invalid IPLD [%s]',
    'ERROR_WHILE_FETCHING_MISSING_FILES': 'Error while fetching missing files for {} entity - ERROR: {}',
    'ERROR_WHILE_CHECKING_WORKSPACE': 'Error while checking workspace data for {} entity - ERROR: {}',
    'ERROR_FILE_DOWNLOAD_FAILED': 'Failed to download file id: [%s]',
    'ERROR_NOT_IN_RESPOSITORY': 'You are not in an initialized ml-git repository.',
    'ERROR_PATH_ALREAD_EXISTS': 'The path [%s] already exists and is not an empty directory.',
    'ERROR_UNABLE_TO_FIND': 'Unable to find %s. Check the remote repository used.',
    'ERROR_UNABLE_TO_FIND_REMOTE_REPOSITORY': 'Unable to find remote repository. Add the remote first.',
    'ERROR_FOLDER_PERMISSION_DENIED': 'Permission denied in folder',
    'ERROR_KEY_PERMISSION_DENIED': 'Permission denied (publickey). Please make sure you have '
                                   'the correct access rights and the repository exists.',
    'ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_GROUP_SIZE': 'The amount parameter should be smaller than the group size.',
    'ERROR_GROUP_SIZE_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE': 'The group size parameter should be smaller than the file list size.',
    'ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP': 'The start parameter should be smaller than the stop.',
    'ERROR_STOP_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE': 'The stop parameter should be smaller than or equal to the file list size.',
    'ERROR_STEP_PARAMETER_SHOULD_BE_SMALLER_STOP': 'The step parameter should be smaller than the stop.',
    'ERROR_GROUP_SIZE_PARAMETER_SHOULD_BE_GREATER_ZERO': 'The group size parameter should be greater than zero.',
    'ERROR_FREQUENCY_PARAMETER_SHOULD_BE_GREATER_ZERO': 'The frequency parameter should be greater than zero.',
    'ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_FREQUENCY': 'The amount parameter should be smaller than the frequency.',
    'ERROR_FREQUENCY_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE': 'The frequency  parameter should be smaller than the file list size.',
    'ERROR_PERMISSION_DENIED_INITIALIZE_DIRECTORY': 'Permission denied. You need write permission to initialize ml-git in this directory.',
    'ERROR_AMOUNT_FREQUENCY_REQUIRES_POSITIVE': 'The --random-sample=<amount:frequency> --seed=<seed>: requires positive integer values.',
    'ERROR_AMOUNT_GROUP_REQUIRES_POSITIVE': 'The --group-sample=<amount:group-size> --seed=<seed>: requires positive integer values.',
    'ERROR_START_STOP_REQUIRES_POSITIVE': 'The --range-sample=<start:stop:step> or  --range-sample=<start:stop>: requires positive integer values.',
    'ERROR_AMOUNT_PARAMETER_SHOULD_BE_GREATER_ZERO': 'The amount parameter should be greater than zero.',
    'ERROR_NO_CURRENT_TAG_FOR': 'No current tag for [%s]. commit first.',
    'ERROR_EMPTY_FILE_LIST': 'The file list is empty.',
    'ERROR_START_PARAMETER_SHOULD_BE_GREATER_ZERO': 'The start parameter should be greater than or equal to zero.',
    'ERROR_RANGE_SAMPLE_START_STOP': 'The --range-sample=<start:stop:step> or  --range-sample=<start:stop>:'
                                      ' requires positive integer values. The stop parameter can be \'all\', \'-1\' or any integer greater than zero',
    'ERROR_PARAMETER_CANNOT_BE_NONE': 'The sample parameter cannot be None',
    'ERROR_WRONG_NAME': 'The entity name passed is wrong. Please check again',
    'ERROR_TAG_INVALID_FORMAT': 'Tag %s invalid format.',
    'ERROR_CANNOT_CREATE_AZURE_CONTAINER': 'Can\'t create Azure container.',
    'ERROR_BLOB_NOT_FOUND': 'Blob not found!',
    'ERROR_WORKER_POOL_EXCEPTION': 'worker pool exception',
    'ERROR_FILE_NOT_FOUND': 'File %s not found',
    'ERROR_GIT_REMOTE_AUTHENTICATION_FAILED': 'Authentication failed for git remote',
    'ERROR_TAG_ALREADY_EXISTS_CONSIDER_USER_VERSION': 'Tag [%s] already exists in the ml-git repository.\n  '
                                                      'Consider using --version parameter to set the version number for your [%s].',
    'ERROR_INCREMENTING_VERSION': '\nError incrementing version.  Please manually examine this file and make sure'
                                  ' the version is an integer:\n'
                                  '%s\n',
    'ERROR_INVALID_SPEC_VALUE_IN': 'Invalid %s spec in %s.  It should look something like this:\n%s',
    'ERROR_SPEC_FILE_NOT_FOUND': '\nCan\'t find  spec file to increment version.  Are you in the '
                                  'root of the repo?\n     %s\n',
    'ERROR_COMMIT_BEFORE_PUSH': 'It is necessary commit the changes before push.',
    'ERROR_ON_PUSH_BLOBS': 'There was an error sending the data. %s pending blobs to send.',
    'ERROR_ON_GETTING_BLOBS': 'There was an error downloading the data. %s pending blobs to get.',
    'ERROR_CANNOT_RECOVER': 'It was not possible to recover from the error found. Please fix the problem and rerun the command again.',
    'ERROR_FOUND': 'ERROR FOUND: %s - %s',
    'ERROR_PUSH_CONFIG': 'Could not push configuration file. ERROR: %s',
    'ERROR_FIND_FILE_PATH_LOCATION': 'A complete log of this run can be found in: %s',
    'ERROR_EMPTY_VALUE': 'Value cannot be empty.',
    'ERROR_NOT_INTEGER_VALUE': '{} is not a valid integer.',
    'ERROR_VALUE_NOT_IN_RANGE': '{} is not in the valid range of {} to {}.',
    'ERROR_INVALID_VALUE': 'The value \'{}\' is invalid. A category cannot contain blank space, special characters, and punctuation characters.',
    'ERROR_REQUIRED_OPTION_MISSING': 'The option `{}` is required if `{}` is used. Please, inform the value for the `{}`',
    'ERROR_TAGS_NOT_MATCH_WITH_ENTITY': 'The tags do not match the entity name',
    'ERROR_INVALID_METRICS_FILE': 'It was not possible to obtain the metrics from the informed file, please check if the file is correctly formatted.',
    'ERROR_ENTITY_NOT_FIND': 'Could not find an entity with the name \'{}\'. Please check again.',
    'ERROR_INVALID_VALUE_FOR_ENTITY': 'The value \'{}\' is invalid. An entity cannot contain blank space, underline, '
                                      'special characters, and punctuation characters.',
    'ERROR_OPTION_WITH_MULTIPLE_VALUES': 'Multiple options are not accepted! The option should only take one value.',
    'ERROR_COMMIT_WITHOUT_ADD': 'Nothing to commit (create/add files and use "ml-git {} add" command to track them)',
    'ERROR_STORAGE_TYPE_INPUT_INVALID': "invalid choice: {}. (choose from s3h, azureblobh, gdriveh, sftph)",
    'ERROR_BADLY_FORMATTED_URL': 'Badly formatted url {}',
    'ERROR_INVALID_ENTITY_DIR': 'The entity data directory must be inside the ml-git project entities directory. \'{}\' is not a valid value.',
    'ERROR_INVALID_FILE': 'Could not find the file [{}] in the entity [{}]. Please check the given path and the entity.',
    'ERROR_INVALID_CONFIG_ARGUMENT': '{} is not a valid config argument.',
    'ERROR_MISSING_CONFIG_ARGUMENT': 'Missing {} config argument.',

    'WARN_CORRUPTED_CANNOT_BE_ADD': 'The following files cannot be added because they are corrupted:',
    'WARN_HAS_CONFIGURED_REMOTE': 'YOU ALREADY HAVE A CONFIGURED REMOTE. All data stored in this repository will be sent to the new one on the first push.',
    'WARN_STORAGE_NOT_IN_CONFIG': 'Storage [%s://%s] not found in configuration file.',
    'WARN_EXCPETION_CREATING_STORAGE': 'Exception creating storage -- Configuration not found for bucket [%s]. '
                                       'The available buckets in config file for storage type [%s] are: %s',
    'WARN_REMOVING_FILES_DUE_TO_FAIL': 'Removing %s files from storage due to a fail during the push execution.',
    'WARN_CANNOT_INITIALIZE_METADATA_FOR': 'Could not initialize metadata for %s. %s',
    'WARN_WORKER_EXCEPTION': 'Worker exception - [%s] -- retry [%d]',
    'WARN_NOT_EXIST_FOR_RELATED_DOWNLOAD': 'Repository: the %s does not exist for related download.',
    'WARN_NOT_FOUND': '[%s] Not found!',
    'WARN_FILE_EXISTS_IN_REPOSITORY': 'The file %s already exists in the repository. If you commit, the file will be overwritten.',
    'WARN_REPOSITORY_NOT_FOUND_FOR_ENTITY': 'No repositories found for %s, verify your configurations!',
    'WARN_USELESS_OPTION': 'Ignoring option `--{}` because it is only needed when using `--{}` option.',
    'WARN_EMPTY_ENTITY': 'The entity %s has no data to be checked. You have to commit some data before executing this command.',
    'WARN_UNCHANGED_FILE': 'The file `{}` has no changes to be submitted.',
    'WARN_SAME_MUTABILITY': 'The entity is already configured with the desired mutability type.'
}
