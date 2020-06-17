################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

$current_dir = "$(get-location);"

$environment_path = [System.Environment]::GetEnvironmentVariable('Path',[System.EnvironmentVariableTarget]::User)

$old_environment_path = $environment_path.Replace($current_dir,"")

# Remove directory from environment variable Path for current user
[System.Environment]::SetEnvironmentVariable('Path', $old_environment_path, [System.EnvironmentVariableTarget]::User)