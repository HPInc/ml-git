::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::: MAIN ::::::::::::::::::::::::::::::::::::::::::::
SET "TESTS_TO_RUN="
SET INTEGRATION_TESTS_BASE_PATH=%cd%\tests\integration
SET IGNORE_TESTS="--ignore=%INTEGRATION_TESTS_BASE_PATH%/gdrive_store"

SET PATH_TEST=%INTEGRATION_TESTS_BASE_PATH%\.test_env
SET MINIO_ACCESS_KEY=fake_access_key						    
SET MINIO_SECRET_KEY=fake_secret_key	                    

@ECHO OFF
:: Processing arguments
FOR %%A IN (%*) DO (
    CALL :PROCESS_ARGUMENTS "%%A"
)

:: If TESTS_TO_RUN was not set yet (through arguments), set it as base path
IF "%TESTS_TO_RUN%"=="" (
    SET TESTS_TO_RUN = %INTEGRATION_TESTS_BASE_PATH%
)
@ECHO ON

docker stop minio1 && docker rm minio1
docker stop azure && docker rm azure
RMDIR /S /Q %PATH_TEST%

MKDIR "%PATH_TEST%/data/mlgit"
MKDIR "%PATH_TEST%/test_permission"
ECHO y| CACLS "%PATH_TEST%/test_permission" /g "%USERNAME%":R

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

:: Installs ml-git itself in the virtualenv to use on Integration Tests
pipenv run python setup.py install

pipenv run pytest ^
    -v ^
    --cov ^
    --cov-report html:%INTEGRATION_TESTS_BASE_PATH%\integration_tests_coverage ^
    --cov-report xml:%INTEGRATION_TESTS_BASE_PATH%\integration_tests_coverage.xml ^
    %TESTS_TO_RUN% %IGNORE_TESTS%

docker stop minio1 && docker rm minio1
docker stop azure && docker rm azure

ECHO y| CACLS "%PATH_TEST%" /g "%USERNAME%":F
RMDIR /S /Q %PATH_TEST%

EXIT /B 0
:::::::::::::::::::::::::::::::::::::::::::: END MAIN ::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::: SUBROUTINES ::::::::::::::::::::::::::::::::::::::::::::
:PROCESS_ARGUMENTS
    IF [%1]==["-h"] (
        CALL :PRINT_HELP
        CMD /C EXIT -1073741510
    ) ELSE (
        IF [%1]==["--gdrive"] (
            SET IGNORE_TESTS=""
        ) ELSE (
            SET TESTS_TO_RUN=%TESTS_TO_RUN% %INTEGRATION_TESTS_BASE_PATH%/%1
        )
    )
EXIT /B 0

:PRINT_HELP
    @ECHO OFF
    ECHO usage:
    ECHO    $ run_integration_tests.bat [test_name1.py test_name2.py...] --gdrive
    ECHO.
    ECHO        test_name1.py test_name2.py..., test files path (relative to 'tests/integration' path)
    ECHO        --gdrive, run integration tests for gdrive store (use this only if you have configured gdrive credentials).
    ECHO.
    ECHO Example 1 - Running all tests but gdrive tests:
    ECHO     $ run_integration_tests.bat
    ECHO.
    ECHO Example 2 - Running all tests (including gdrive tests):
    ECHO     $ run_integration_tests.bat --gdrive
    ECHO.
    ECHO Example 3 - Running tests/integration/test01.py and tests/integration/test02.py along with gdrive tests:
    ECHO     $ run_integration_tests.bat test01.py test02.py --gdrive
    ECHO.
    ECHO Example 4 - Running only tests/integration/test01.py and tests/integration/test02.py:
    ECHO     $ run_integration_tests.bat test01.py test02.py
    @ECHO ON
EXIT /B 0