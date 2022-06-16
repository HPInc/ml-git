[33mcommit 2108c181ba2856cea5c1b016b0bea80acc2a0115[m[33m ([m[1;36mHEAD -> [m[1;32mbugfix/32095[m[33m)[m
Author: MatheusClaudi <matheus.claudino@ccc.ufcg.edu.br>
Date:   Thu Jun 16 16:59:09 2022 -0300

    Adding use for wizard when user inform invalid storage type

[33mcommit d5bc09e82bc5acc791cbac9ee8af241aa066ce1d[m[33m ([m[1;33mtag: 2.7.1-alpha[m[33m, [m[1;31morigin/development[m[33m, [m[1;32mdevelopment[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Thu Jun 16 08:03:47 2022 -0300

    Update version to 2.7.1

[33mcommit 59f33c4103c874db612e104da8c4f487ffcec92f[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Thu Jun 16 07:53:06 2022 -0300

    Adding method to validate the input in the wizard-config option of create (#223)
    
    * Adding method to validate the input in the wizard-config option of create

[33mcommit cc53401c9c0bc8d7b1b74fe7ef915454e1d47a8a[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Thu Jun 16 07:45:50 2022 -0300

    Removing tag option from commit command (#224)

[33mcommit 1f4b7dbc532561a813ad4c4a4abe79d5cd28d40a[m
Author: MatheusClaudi <51119782+MatheusClaudi@users.noreply.github.com>
Date:   Wed Jun 15 10:36:11 2022 -0300

    Adding use of wizard to port on SFPTH storage (#219)
    
    * Adding use of wizard to port on sfpth storage
    
    * Update ml_git/commands/wizard.py
    
    Co-authored-by: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>

[33mcommit fd16326bbc3a95acc1b906f358994eeb842fd190[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Wed Jun 15 10:25:20 2022 -0300

    Adding validation for multiple values in related entities options (#220)
    
    * Adding validation for multiple values in related entities options
    
    * Adding integration tests
    
    Co-authored-by: andersonpablosilva <andersonpablo@gmail.com>

[33mcommit a1b8937df40351c0a5422ce3c91608293fc15020[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Wed Jun 15 08:03:55 2022 -0300

    Adding treatment for commit attempt with no data to commit (#221)
    
    * Adding treatment for commit attempt with no data to commit
    
    * Adding and updating integration tests

[33mcommit 9b5890f6b7ee45c44258f6b3a280a53ec0432916[m[33m ([m[1;33mtag: 2.7.0-alpha[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Thu Jun 9 12:10:33 2022 -0300

    Update version to 2.7.0

[33mcommit e9de70d49bf102a03de89b236fd243f41437711a[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Wed Jun 8 17:36:22 2022 -0300

     Adding the wizard option to commands that support it (#218)
    
    * Adding --wizard option in commands
    
    * Adding integration tests

[33mcommit 251e2531148204cf02936cb20a128b5e27bd9531[m
Author: Gilmar Bezerra <gilmar.lilium@gmail.com>
Date:   Wed Jun 8 17:30:59 2022 -0300

    Adjustment to deploy ml-git release in pypi repository. (#119)
    
    * Added distribution upload action
    
    * Updating setup.py to use README.md as long description
    
    Co-authored-by: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>

[33mcommit 61449278a6800ae6d331763906da912b216418c0[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Tue Jun 7 16:36:22 2022 -0300

    Adding command that allows enabling and disabling the wizard (#216)
    
    * Adding command that allows enabling and disabling the wizard
    
    * Updating config commands validation

[33mcommit 8d7a1638504c0768bf64db0a48bf25c3378f078d[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Tue May 31 07:46:49 2022 -0300

    Update version to 2.6.1

[33mcommit 653888f4a0604c5efaa96a9bb1f167673bfef772[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon May 30 21:20:36 2022 -0300

    Adding validation to empty import_url option (#215)

[33mcommit 79b354adc52082823b7f2ef20b764ae8d06763cc[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon May 30 21:19:31 2022 -0300

    Adding validation for related entities in the commit command (#214)
    
    * Adding validation to related entities
    
    * Updating integration tests

[33mcommit d87acfc09a07fa29876f4c9184418d2fa2129eaf[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon May 30 18:18:23 2022 -0300

    Prompting endpoint URL when adding an sftp storage and setting aws default region (#213)
    
    * Prompting URL when adding an sftp storage
    
    * Setting AWS default region and updating integration tests

[33mcommit 9d4cdae606ba4e8a5c0efda5efc735cdc9c01913[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon May 30 15:54:37 2022 -0300

    Updating the error message when identifying an invalid category (#212)

[33mcommit 8653abef4f5b9aaed21902cd941cf5f390796c11[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Fri May 27 14:44:49 2022 -0300

    Prompt user for values for dependent options (#211)
    
    * Prompt user for values for dependent options
    
    * Removing unnused import

[33mcommit 3130e75d4fce93b809139767dbf9739268ebce1b[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Thu May 26 09:41:55 2022 -0300

    Setting the fsck option as a flag in the commit command (#210)

[33mcommit ad28eacbb7565bac323e0b407caa691872721aa6[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Wed May 25 07:47:13 2022 -0300

    Updating version to 2.6.0

[33mcommit 20c09faa342353b2e5bd333818d04419ef711102[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Tue May 24 18:01:01 2022 -0300

    Adding wizards to command options (#208)
    
    * Adding wizard to commands
    
    * Updating tests
    
    * Updating documentation messages
    
    * Adding testes for commit wizard
    
    Co-authored-by: Vieira-Carlos <100164418+Vieira-Carlos@users.noreply.github.com>
    Co-authored-by: Lucas <lucas.cabral@ccc.ufcg.edu.br>
    Co-authored-by: MatheusClaudi <51119782+MatheusClaudi@users.noreply.github.com>

[33mcommit 0dbdc171e390d85ae794563126f59b5a505bd681[m[33m ([m[1;33mtag: 2.5.2-alpha[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Tue Mar 8 17:48:47 2022 -0300

    Update version to 2.5.2

[33mcommit 2adc655154b85c83aceb581537d755240195a783[m
Author: Vieira-Carlos <100164418+Vieira-Carlos@users.noreply.github.com>
Date:   Tue Mar 8 17:47:24 2022 -0300

    Changing the log level for Corruption Detected messages on the remote… (#206)
    
    * Changing the log level for Corruption Detected messages on the remote fsck --paranoid command
    
    * Changing msg name from ERROR to DEBUG

[33mcommit ce049edd44434078173d7da557867987329b6240[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Tue Mar 8 17:36:38 2022 -0300

    Adding validation to check if the user is in a valid directory when running the add command (#207)

[33mcommit 7231c69361a8297d74cbd148eda6d895716385f7[m[33m ([m[1;33mtag: 2.5.1-alpha[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Tue Mar 8 09:58:30 2022 -0300

    Update version to 2.5.1

[33mcommit 27c5548bbfa128814110eccfc8c708cb6a780ca5[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Tue Mar 8 09:54:48 2022 -0300

    Adding message to show the list of missing IPLD (#204)
    
    * Adding message to show the list of missing IPLD
    
    * Removing blank space
    
    * Fixing integration tests
    
    * Fixing flake8 issue
    
    * Removing cast to string
    
    * Updating integratio test

[33mcommit 56844093ece6bbf023be7dec91db8240d2a17cbb[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon Mar 7 18:58:54 2022 -0300

    Adding treatments for repository and uninitialized entity in fsck command (#205)

[33mcommit f522d3317a34ea8951608351a21c7627db45c386[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon Mar 7 18:36:06 2022 -0300

    Adding handling for invalid csv file in add command (#203)
    
    * Adding handling for invalid csv file in add command
    
    * Update ml_git/ml_git_message.py
    
    Co-authored-by: Vieira-Carlos <100164418+Vieira-Carlos@users.noreply.github.com>
    
    Co-authored-by: Vieira-Carlos <100164418+Vieira-Carlos@users.noreply.github.com>

[33mcommit 87c62e25d30cfb8e31f269759a9df612494ba2ca[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon Mar 7 16:37:15 2022 -0300

    Adding message when executing remote-fsck for empty entity (#201)
    
    * Adding message when executing remote-fsck for empty entity
    
    * Updating unit and integration tests

[33mcommit 8a3404aeb1fd31ae4e436c009c7ddd6a61628cb7[m
Author: Lucas Cabral <lucas.cabral@ccc.ufcg.edu.br>
Date:   Mon Mar 7 15:03:48 2022 -0300

    Add validation for empty string in metrics-file option (#202)

[33mcommit fa19b084622e871c8596a5939f70a2ac4bba4153[m[33m ([m[1;33mtag: 2.5.0-alpha[m[33m)[m
Author: andersonpablosilva <andersonpablo@gmail.com>
Date:   Thu Mar 3 15:49:17 2022 -0300

    Updates file lists options in commands output (#200)
    
    * Update fsck command output (#194)
    
    * Update add command output when it has corrupt files (#195)
    
    * Update checkout command output when it has unsaved files (#196)
    
    * Update remote-fsck command output (#197)
    
    * Update documentation to reflect changes in command outputs (#198)
    
    * Update log command (#199)
    
    * Update version to 2.5.0
    
    Co-authored-by: Lucas <lucas.cabral@ccc.ufcg.edu.br>
    Co-authored-by: Vieira-Carlos <100164418+Vieira-Carlos@users.noreply.github.com>
    Co-authored-by: MatheusClaudi <51119782+MatheusClaudi@users.noreply.github.com>

[33mcommit 461ea6a6e131fad9ebc53156b1eb7aec660ffade[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Thu Dec 9 11:54:15 2021 -0300

    Updating documentation to include other storages (#193)

[33mcommit 8e7e03811e486e0a4d25f0b3e5116bd0b0d667a8[m[33m ([m[1;33mtag: 2.4.2-alpha[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Thu Nov 11 17:14:42 2021 -0300

    Update ml-git version to 2.4.2

[33mcommit 74d1eba8599d2941271a110e2b0963fa3b90dd4a[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Thu Nov 11 16:16:06 2021 -0300

    Updating diff methods to compare MANIFEST files (#192)
    
    * Updating diff methods to compare MANIFEST files
    
    Co-authored-by: gilMars <gilmar.lilium@gmail.com>

[33mcommit c2d9bfee7391f62034b0ad7d47746fb89827834f[m[33m ([m[1;33mtag: 2.4.1-alpha[m[33m)[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Wed Nov 10 08:12:56 2021 -0300

    Update version to 2.4.1

[33mcommit 51bb31c214a30efa09f4d36e57f4c5b998cb7c6c[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Tue Nov 9 17:09:58 2021 -0300

    Fix the output of the diff command (#191)
    
    * Updating add command logic to work properly
    
    * Adding integration tests

[33mcommit ab1b29d9e6c0dd505e16605b8758da103f0c71f7[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Tue Nov 9 12:01:51 2021 -0300

    Define versions for dependencies on Github Actions and use GitHub composite actions (#190)
    
    * Defining versions of dependencies and using GitHub composite actions

[33mcommit bfc8f356247e07527cc0e1008659edd083687c8c[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Tue Nov 9 11:43:11 2021 -0300

    Fix unpublished commits count in status command (#189)
    
    * Fixing unpublished commits count in status command

[33mcommit a010f7b96e0f36c4bfe1b1271275227e44a21bd2[m[33m ([m[1;33mtag: 2.4.0-alpha[m[33m)[m
Author: Lucas <lucas.cabral@ccc.ufcg.edu.br>
Date:   Wed Nov 3 08:44:31 2021 -0300

    Update version to 2.4.0

[33mcommit bee97254f4070f8713cd921b7d2f3aee54490650[m
Author: Felipe Muniz <felipemuniznet@gmail.com>
Date:   Tue Nov 2 18:15:21 2021 -0300

    Create a Jupyter Notebook example on how to work with the MLGitAPI class (#185)
    
    * Creation of multiple projects notebook example
    
    Co-authored-by: Felipe Muniz <felipemuniz.net@gmail.com>
    Co-authored-by: Tales Satiro <talessatiro@gmail.com>

[33mcommit d66bbb87b422d129dc04c62b502a02accd63f0f9[m
Author: Tales Satiro <talessatiro@gmail.com>
Date:   Tue Nov 2 14:47:14 2021 -0300

    Diff command implementation (#187)
    
    * create diff command
    
    * insert documentation about diff command
    
    Co-authored-by: gilMars <gilmar.lilium@gmail.com>
    Co-authored-by: andersonpablosilva <andersonpablo@gmail.com>
    Co-authored-by: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>

[33mcommit 4bc3d0a36d5d854ec2b4794dd75605de9d79e828[m
Author: Gustavo Nunes <gm.nunes92@gmail.com>
Date:   Tue Nov 2 12:42:27 2021 -0300

    Create MLGitAPI to allow multiple projects in the same script (#181)
    
    * Creating MLGitAPI class to allow multiple projects in the same file
    
    * Updating documentation and Jupyter notebooks to work with the MLGitAPI class
    
    Co-authored-by: Felipe Muniz <felipemuniz.net@gmail.com>
    Co-authored-by: andersonpablosilva <andersonpablo@gmail.com>

[33mcommit 4f0e3a360e023f2a3b3b97706cced7df7e0e3827[m
Merge: 76ce67d ed65cf7
Author: andersonpablosilva <andersonpablo@gmail.com>
Date:   Tue Nov 2 12:24:02 2021 -0300

    Merge pull request #188 from HPInc/bugfix/2.3.4
    
    Patch 2.3.4

[33mcommit ed65cf7319c5f443c2ba30f2a9fa603ffba2a01b[m[33m ([m[1;33mtag: 2.3.4-alpha[m[33m)[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Wed Sep 29 18:27:21 2021 -0300

    Avoid creating a default bucket when initializing a project (#179)
    
    * Removing default bucket creation when initializing a project
    
    * Updating config example in gdrive_configurations file

[33mcommit 0bfed559131338b61d0704d802587c5ec1014457[m
Author: Anderson Pablo <andersonpablo@gmail.com>
Date:   Wed Sep 29 17:30:02 2021 -0300

    Update version to 2.3.4

[33mcommit 76ce67df8ba7c321dee0529881275abbf63affaf[m
Merge: 0dd388d 6e00c40
Author: andersonpablosilva <andersonpablo@gmail.com>
Date:   Wed Sep 29 16:52:27 2021 -0300

    Merge pull request #178 from HPInc/bugfix/2.3.3
    
    Patch 2.3.3

[33mcommit 0dd388dec1fdc4f559e389c2a558b5b9e23c95ce[m
Merge: de14944 977deca
Author: andersonpablosilva <andersonpablo@gmail.com>
Date:   Wed Sep 29 14:28:12 2021 -0300

    Merge pull request #177 from HPInc/bugfix/2.3.2
    
    Patch 2.3.2

[33mcommit 6e00c40aef5bf9a6c19a676fac24cc6533161bce[m[33m ([m[1;33mtag: 2.3.3-alpha[m[33m)[m
Author: Gilmar Bezerra <gilmar.lilium@gmail.com>
Date:   Wed Sep 29 14:25:52 2021 -0300

    Remove special characters from commands in the documentation (#174)
    
    * Removing special characters from commands in the documentation

[33mcommit 977decaffdc177464e7eed3cfb29a8dfa5ecffd4[m[33m ([m[1;33mtag: 2.3.2-alpha[m[33m)[m
Author: Felipe Muniz <felipemuniznet@gmail.com>
Date:   Tue Sep 28 22:32:57 2021 -0300

    Add custom type to validate empty strings in entity-dir param of create commend (#170)
    
    * Adding custom type to validate empty strings
    
    * Adding documentation for the custom types
    
    * Addition of empty string validor on --entity-dir
    
    Co-authored-by: Gustavo Maciel <gustavo.nunes@hp.com>
    Co-authored-by: Felipe Muniz <felipemuniz.net@gmail.com>
    Co-authored-by: Anderson Pablo <andersonpablo@gmail.com>

[33mcommit e3cf1ed61e61225c9a2e48fa56c7376ac1d2b663[m
Author: Tales Satiro <talessatiro@gmail.com>
Date:   Tue Sep 28 21:09:28 2021 -0300

    Fix issue related to storage type s3h being saving in global configuration instead of local configuration (#175)
    
    * fix issue related to storage being saving in global configuration

[33mcommit cfaa0bbc77fe1bb24f2102fbb93e5086ca87677c[m
Author: André Gomes <33471054+andregom@users.noreply.github.com>
Date:   Tue Sep 28 20:06:48 2021 -0300

    Add info message when .spec is added automatically to staged files (#167)
    
    * Add info message when automatically add spec file
    
    * Show info message when user use bumpversion
    
    * Update commit integration tests
    
    Co-authored-by: Lucas <lucas.cabral@ccc.ufcg.edu.br>
    Co-authored-by: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>

[33mcommit 07cf270809e7975c83ffe5f533ef7dc6282e999d[m
Author: Lucas Cabral <lucas.cabral@virtus.ufcg.edu.br>
Date:   Tue Sep 28 19:28:23 2021 -0300

    Fix the problem of configuring an sftp bucket with the wizard option (#173)
    
    * Refactoring wizard config methods
    
    * Update list to use MultihashStorageType
    
    * Update wizard config unit tests
    
    * Update wizard messages and improving readability
