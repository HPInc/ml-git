#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

set -e
set -x

INTEGRATION_TESTS_BASE_PATH=$PWD/tests/integration
IGNORE_TESTS="--ignore=$INTEGRATION_TESTS_BASE_PATH/gdrive_storage"

usage()
{
    {
      echo "usage:
          $ run_integration_tests.sh [<test_name1.py> <test_name2.py>...] --gdrive
              <test_name1.py> <test_name2.py>..., test files path (relative to 'tests/integration' path)
              --gdrive, run integration tests for gdrive storage (use this only if you have configured gdrive credentials).

          Example 1 - Running all tests but gdrive tests:
              $ run_integration_tests.sh

          Example 2 - Running all tests (including gdrive tests):
              $ run_integration_tests.sh --gdrive

          Example 3 - Running tests/integration/test01.py and tests/integration/test02.py along with gdrive tests:
              $ run_integration_tests.sh test01.py test02.py --gdrive

          Example 4 - Running only tests/integration/test01.py and tests/integration/test02.py:
              $ run_integration_tests.sh test01.py test02.py"
    } 2> /dev/null
}

update_tests_to_run()
{
  TESTS_TO_RUN="$TESTS_TO_RUN $INTEGRATION_TESTS_BASE_PATH/$1"
}

while [ "$1" != "" ]; do
    case $1 in
      --gdrive)
        IGNORE_TESTS=
        ;;
      -h | --help)
        usage
        exit 0
        ;;
      *)
        update_tests_to_run "$1"
        ;;
    esac
    shift
done

# If no specific test was set, set base path to run
if [ -z "$TESTS_TO_RUN" ]
then
      TESTS_TO_RUN=$INTEGRATION_TESTS_BASE_PATH
fi

PATH_TEST=$INTEGRATION_TESTS_BASE_PATH/.test_env
MINIO_ACCESS_KEY=fake_access_key
MINIO_SECRET_KEY=fake_secret_key
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure
docker stop sftp && docker rm sftp

rm -rf $PATH_TEST
mkdir -p $PATH_TEST/data/mlgit
mkdir $PATH_TEST/test_permission
mkdir -p $PATH_TEST/sftp/mlgit
chmod -R 777 $PATH_TEST/sftp/mlgit
chmod -w $PATH_TEST/test_permission

docker run -p 9000:9000 --name minio1 \
--user $(id -u):$(id -g) \
-e "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
-e "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
-v $PATH_TEST/data:/data \
minio/minio:RELEASE.2022-05-26T05-48-41Z.hotfix.15f13935a server /data &

docker run -p 10000:10000 --name azure \
-v $PATH_TEST/data:/data  \
mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0 &

rm -rf $INTEGRATION_TESTS_BASE_PATH/fake_ssh_key/
mkdir -p $INTEGRATION_TESTS_BASE_PATH/fake_ssh_key/

ssh-keygen -t rsa -N "" -b 4096 -f $INTEGRATION_TESTS_BASE_PATH/fake_ssh_key/test_key

docker run --name=sftp -v $INTEGRATION_TESTS_BASE_PATH/fake_ssh_key/test_key.pub:/home/mlgit_user/.ssh/keys/test_key.pub:ro \
-v $PATH_TEST/sftp/mlgit:/home/mlgit_user/mlgit \
-p 9922:22 -d atmoz/sftp \
mlgit_user::1001:::mlgit

sleep 10s

pipenv install --ignore-pipfile --dev
pipenv run pip freeze

# Installs ml-git itself in the virtualenv to use on integration tests
pipenv run pip install -e .

pipenv run pytest \
    -n auto \
    --dist=loadscope \
    -v \
    --cov=ml_git \
    --cov-report html:$INTEGRATION_TESTS_BASE_PATH/integration_tests_coverage \
    --cov-report xml:$INTEGRATION_TESTS_BASE_PATH/integration_tests_coverage.xml \
    -o junit_family=xunit1 --junitxml=$INTEGRATION_TESTS_BASE_PATH/integration_tests_report.xml \
    $TESTS_TO_RUN $IGNORE_TESTS

chmod +w $PATH_TEST
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure
docker stop sftp && docker rm sftp
