# First install and bootstrap

`firstInstall.sh plan` and the default `bootstrap.sh` invocation are read-only
previews. `bootstrap.sh --apply` applies the fixed Debian/Ubuntu package plan,
installs the exact committed checkout into a private prefix and verifies its
manifest.

```sh
mkdir -p "$HOME/.local/opt"
# Optional separate planner when Python 3.10+ is already available:
./firstInstall.sh plan
# This bootstrap preview also works when Python is not installed yet:
./bootstrap.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
# Review the printed plan, then explicitly apply it:
./bootstrap.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA --apply
```

The checkout must be clean and its HEAD must match the supplied 40-character
commit. The bootstrap uses Python 3.10+ to plan. If it is missing, the first
`--apply` installs only Python 3 on Debian/Ubuntu and stops after printing the
complete package plan. Review that plan, then invoke `--apply` again. All other
package installation requires root or noninteractive `sudo`; the bootstrap
will not pause for a password. The default includes `fd`/`fdfind`, ShellCheck,
hyperfine and Linux-only strace. `--profile debug` remains a compatibility
alias. PHP and Composer remain project managed and are never installed by this
flow.

The bootstrap does not edit shell startup files, login shells or global Git
configuration. Source `activate.sh` explicitly for a task shell. It selects
Bash or Zsh, applies the same additive per-process Git defaults and can be
reversed with `agent_deactivate`. Full patches, errors and context remain
visible.

`install.sh plan` previews the pinned payload; `install.sh verify` validates
the installed manifest. `install.sh uninstall` removes only a verified prefix.
The Python code behind the manifest installer is maintainer plumbing, not an
agent-facing CLI.
