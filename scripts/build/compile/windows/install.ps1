################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

$current_dir = "$(get-location);"

$environment_path = [System.Environment]::GetEnvironmentVariable('Path',[System.EnvironmentVariableTarget]::User)

$new_environment_path = $current_dir+$environment_path


# Change environment variable Path for current user
[System.Environment]::SetEnvironmentVariable('Path', $new_environment_path, [System.EnvironmentVariableTarget]::User)