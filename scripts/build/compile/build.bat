::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

pipenv uninstall --all
pipenv install --ignore-pipfile --dev
pipenv run python -O -m PyInstaller -D -n ml-git ./ml_git/main.py

mkdir dist\ml-git
COPY .\scripts\build\compile\windows\install.ps1 dist\ml-git
COPY .\scripts\build\compile\windows\uninstall.ps1 dist\ml-git

set datetimef=%date:~-4%%date:~3,2%%date:~0,2%
echo BUILD_NUMBER=%datetimef%>build/version.info

for /f "delims== tokens=1,2" %%G in (%cd%/version.info) do set %%G=%%H
set BUILD_VERSION=%MAJOR_VERSION%.%MINOR_VERSION%.%PATCH_VERSION%

set BUILD_NAME=%BUILD_VERSION%-%datetimef%

tar -cvzf ".\dist\ml_git_%BUILD_NAME%_Windows.tar.gz" -C .\dist ml-git
