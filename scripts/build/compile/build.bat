::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

pipenv install --ignore-pipfile --dev
pipenv run python -O -m PyInstaller -D -n ml-git ./ml_git/main.py

COPY .\scripts\build\compile\windows\install.ps1 dist\ml-git
COPY .\scripts\build\compile\windows\uninstall.ps1 dist\ml-git

for /f "tokens=*" %%i in ('pipenv run ml-git --version') do set build_name=%%i

tar -cvzf ".\dist\%build_name%_Windows.tar.gz" -C .\dist ml-git