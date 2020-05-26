Development Guide
=====================

1. At the project root directory, run build script accordingly with the Operating System:

   * **Linux:**

     ```bash
     ./compile/build.sh
     ```

    * **Windows:**

      ```bash
      .\compile\build.bat
      ```

2. After the building process finishes you can distribute the file "ml-git \<build_version\>_\<operating_system\>.tar.gz" created at ```dist``` directory.

Installation Guide
==================

### Windows

1. Extract the file "ml-git \<build_version\>_Windows.tar.gz" to the directory you choose to be the installation folder.
2. Navigate to **ml-git** folder and execute `install.ps1` with PowerShell.

*To uninstall the **ml-git** go to ml-git folder and execute `uninstall.ps1` with PowerShell.*

### Linux

1. Extract the file "ml-git \<build_version\>_Linux.tar.gz" to the directory you choose to be the installation folder.
2. Navigate to **ml-git** folder and execute **sudo sh install.sh** in Terminal.

*To uninstall the **ml-git** go to ml-git folder and execute `sudo sh uninstall.sh` with Terminal.*
