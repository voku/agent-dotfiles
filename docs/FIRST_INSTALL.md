# First install and bootstrap

`firstInstall.sh plan` remains a read-only preview of missing host tools. The
native setup path for a fresh Debian/Ubuntu machine is `bootstrap.sh`; it uses
the same fixed package allowlist, installs missing packages noninteractively,
installs the exact committed checkout into a private prefix and verifies its
manifest.

```sh
mkdir -p "$HOME/.local/opt"
./firstInstall.sh plan
./bootstrap.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
```

The checkout must be clean and its HEAD must match the supplied 40-character
commit. `apt-get` and Python 3.10+ are setup prerequisites. When packages are
missing, run as root or establish noninteractive `sudo` access; setup will not
pause for a password. The bootstrap supports `--profile debug`
for `fd`, ShellCheck, hyperfine and strace. PHP and Composer remain project
managed and are never installed by this flow.

The bootstrap does not edit shell startup files, login shells or global Git
configuration. Source `activate.sh` explicitly for a task shell. It selects
Bash or Zsh, applies the same additive per-process Git defaults and can be
reversed with `agent_deactivate`. Full patches, errors and context remain
visible.

`install.sh plan` previews the pinned payload; `install.sh verify` validates
the installed manifest. `install.sh uninstall` removes only a verified prefix.
The Python code behind the manifest installer is maintainer plumbing, not an
agent-facing CLI.
