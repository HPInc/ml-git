::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set INTEGRATION_TESTS_BASE_PATH=%cd%\tests\integration
set PATH_TEST=%INTEGRATION_TESTS_BASE_PATH%\.test_env
set MINIO_ACCESS_KEY=fake_access_key						    
set MINIO_SECRET_KEY=fake_secret_key	                    
docker stop minio1 && docker rm minio1
docker stop azure && docker rm azure
RMDIR /S /Q %PATH_TEST%

MKDIR "%PATH_TEST%/data/mlgit"
MKDIR "%PATH_TEST%/test_permission"
echo y| CACLS "%PATH_TEST%/test_permission" /g "%USERNAME%":R

START docker run -p 9000:9000 --name minio1 ^
-e "MINIO_ACCESS_KEY=%MINIO_ACCESS_KEY%" ^
-e "MINIO_SECRET_KEY=%MINIO_SECRET_KEY%" ^
-v "%PATH_TEST%\data:/data" ^
minio/minio server /data

START docker run -p 10000:10000 --name azure ^
-v "%PATH_TEST%\data:/data"  ^
mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0

pipenv install --ignore-pipfile --dev
pipenv run pip freeze

pipenv run pytest ^
    -v ^
    --cov ^
    --cov-report html:%INTEGRATION_TESTS_BASE_PATH%\integration_tests_coverage ^
    --cov-report xml:%INTEGRATION_TESTS_BASE_PATH%\integration_tests_coverage.xml ^
    %INTEGRATION_TESTS_BASE_PATH%

docker stop minio1 && docker rm minio1
docker stop azure && docker rm azure

echo y| CACLS "%PATH_TEST%" /g "%USERNAME%":F
RMDIR /S /Q %PATH_TEST%
