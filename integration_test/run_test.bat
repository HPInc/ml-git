::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

if ["%~1"]==[""] (
	set tests_to_run="."
) else (
	set tests_to_run=%*
)


set PATH_TEST=.test_env
set GIT=%PATH_TEST%/local_git_server.git
set MINIO_ACCESS_KEY=fake_access_key						    
set MINIO_SECRET_KEY=fake_secret_key	                    
docker stop minio1 && docker rm minio1
RMDIR /S /Q %PATH_TEST%
MKDIR "%GIT%"
git init --bare %GIT%
git clone %GIT%/ master
echo '' > master/README.md
git -C master add .
git -C master commit -m "README.md"
git -C master push origin master
RMDIR /S /Q master

MKDIR "%PATH_TEST%/data/mlgit"
MKDIR "%PATH_TEST%/test_permission"
echo y| CACLS "%PATH_TEST%/test_permission" /g "%USERNAME%":R

START docker run -p 9000:9000 --name minio1 ^
-e "MINIO_ACCESS_KEY=%MINIO_ACCESS_KEY%" ^
-e "MINIO_SECRET_KEY=%MINIO_SECRET_KEY%" ^
-v "%CD%\%PATH_TEST%\data:/data" ^
minio/minio server /data

echo "Running tests %tests_to_run%..."
pytest -v --cov=../../src/mlgit --cov-report term-missing --cov-report html:../integration_tests_coverage --cov-report xml:../integration_tests_coverage.xml %tests_to_run%

docker stop minio1 && docker rm minio1
echo y| CACLS "%PATH_TEST%" /g "%USERNAME%":F
RMDIR /S /Q %PATH_TEST%