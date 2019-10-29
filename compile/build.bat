::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

python -O -m PyInstaller -D -n ml-git ../src/mlgit/main.py

COPY windows\install.ps1 dist\ml-git
COPY windows\uninstall.ps1 dist\ml-git