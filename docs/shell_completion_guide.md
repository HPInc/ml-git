
# ML-Git Shell Completion Support #

The Shell completion is a function that allows autocomplete your ml-git commands by typing partially the commands or options, then pressing the `[Tab]` key. This will help you when writing the command in terminal.

The shell completion support will complete commands and options. Options are only listed if at least a dash has been entered.

In order to activate shell completion, you need to inform your shell that completion is available for the ML-Git.
For that, we provide the necessary modifications in the script for each type of terminal that we support the autocompletion:
- [Bash](#bash)
- [Fish](#fish)
- [Windows PowerShell](#powershell)
- [Zsh](#zsh)

**Note**: If you have the shell open before making the modification, you will need to restart it after modifying the script.

#### <a name="bash">For Bash, add this to ~/.bash_completion:</a>

```
_ml-git_completion() {
    local IFS=$'\t'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ML_GIT_COMPLETE=complete-bash $1 ) )
    return 0
}
complete -F _ml-git_completion -o default ml-git
```

#### <a name="fish">For Fish, create the file ~/.config/fish/completions/ml-git.fish and add:</a>
```
complete --command ml-git --arguments "(env _ML_GIT_COMPLETE=complete-fish COMMANDLINE=(commandline -cp) ml-git)" -f
```

#### <a name="powershell">For Windows PowerShell, add this to PowerShell Profile file*:</a>

```
if ((Test-Path Function:\TabExpansion) -and -not (Test-Path Function:\ml-gitTabExpansionBackup)) {
    Rename-Item Function:\TabExpansion ml-gitTabExpansionBackup
}

function TabExpansion($line, $lastWord) {
    $lastBlock = [regex]::Split($line, '[|;]')[-1].TrimStart()
    $aliases = @("ml-git") + @(Get-Alias | where { $_.Definition -eq "ml-git" } | select -Exp Name)
    $aliasPattern = "($($aliases -join '|'))"
    if($lastBlock -match "^$aliasPattern ") {
        $Env:_ML_GIT_COMPLETE = "complete-powershell"
        $Env:COMMANDLINE = "$lastBlock"
        (ml-git) | ? {$_.trim() -ne "" }
        Remove-Item Env:_ML_GIT_COMPLETE
        Remove-Item Env:COMMANDLINE
    }
    elseif (Test-Path Function:\ml-gitTabExpansionBackup) {
        # Fall back on existing tab expansion
        ml-gitTabExpansionBackup $line $lastWord
    }
}
```

*To find out where your PowerShell Profile file is located you can run `$profile` in Windows Powershell.
If you don't already have a profile file, follow the steps described in this link [(How to create a profile)](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.2#how-to-create-a-profile) to create a new one.

#### <a name="zsh">For Zsh, add this to ~/.zshrc:</a>

```
#compdef ml-git
_ml-git() {
  eval $(env COMMANDLINE="${words[1,$CURRENT]}" _ML_GIT_COMPLETE=complete-zsh  ml-git)
}
if [[ "$(basename -- ${(%):-%x})" != "_ml-git" ]]; then  
  compdef _ml-git ml-git
fi
```
