#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

tests_to_run="."
ignore_tests="--ignore=gdrive_store"

usage()
{
    echo "usage:
    --path='tests_path', path with tests to run.
    --gdrive, run integration tests for gdrive store."
}

while [ "$1" != "" ]; do
    case $1 in
      --path=?*)
        tests_to_run=${1#*=}
        ;;
      --gdrive)
        ignore_tests=
        ;;
      -h | --help)
      usage
      exit 1
      ;;
      *)
        exit 1
    esac
    shift
done

PATH_TEST=.test_env
GIT=$PATH_TEST/local_git_server.git
MINIO_ACCESS_KEY=fake_access_key						    
MINIO_SECRET_KEY=fake_secret_key	                    
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure
mkdir -p $GIT
git init --bare $GIT

git clone $GIT/ master
echo '' > master/README.md
git -C master add .
git -C master commit -m "README.md"
git -C master push origin master
rm -rf master

mkdir -p $PATH_TEST/data/mlgit
mkdir $PATH_TEST/test_permission
chmod -w $PATH_TEST/test_permission

docker run -p 9000:9000 --name minio1 \
--user $(id -u):$(id -g) \
-e "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
-e "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
-v $PWD/$PATH_TEST/data:/data \
minio/minio server /data &

docker run -p 10000:10000 --name azure \
-v $PWD/$PATH_TEST/data:/data  \
mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0 &

sleep 10s

pytest -v --cov=../../src/mlgit --cov-report html:../integration_tests_coverage --cov-report xml:../integration_tests_coverage.xml $tests_to_run $ignore_tests

chmod +w $PATH_TEST
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure
