# First install: developer tool capability plan (S0)

The current `firstInstall.sh` is **read-only**. Without an explicit profile
it plans the universal Git, search and utility baseline, not a special
programming environment. It detects binaries and supported platform
package managers and prints one JSON recommendation. It does not
execute a package manager, install tools, change HOME or global Git, or contact
the network. Installation of the agent-dotfiles runtime is separately handled by
[`install.sh`](INSTALLATION.md), using reviewed full Git commits.

```sh
./firstInstall.sh plan
./firstInstall.sh plan --profile php
./firstInstall.sh plan --profile debug
```

`firstInstall.sh` uses its own small **planning selections** for package
recommendations. They are not files, local configuration, shell startup scripts
or the diagnostic `profiles/*.json` catalog used by `doctor`. The baseline
is the default in both commands; legacy `doctor --profile minimal|git|shell`
views do not need selecting to use Git/search/shell capabilities.
`doctor --profile php` and `plan --profile php` both diagnose `php` and
`composer`. The opt-in `doctor --profile debug` checks the same specialized
tools as `plan --profile debug` without installing or running them. The
planner and doctor retain their different JSON schemas and roles:

- `minimal`: Python 3, Git, ripgrep, jq, curl.
- `php`: minimal plus PHP and Composer (detected only: no assumed correct system PHP packages).
- `debug`: minimal plus fd/fdfind, ShellCheck, hyperfine and Linux-only strace.

The wrapper requires Python 3.10 or newer and exits with status `2` and a
clear diagnostic if Python is missing, too old or unusable. It starts only the
Python runtime for its version check and planner; it does not invoke the
probed developer tools. A machine without a working Python must provision that
prerequisite independently.

The command shows `available`, chosen executable name/path, `version: null`
(versions are intentionally not inferred or obtained by executing code), and
`package_command_argv` only for missing known packages on detected Debian/Ubuntu
with `apt-get` or macOS with Homebrew. A suggested command is **not approval**
to execute it. Ubuntu/Debian plans require separate privilege approval; other
Linux distributions and macOS without Homebrew get explicit missing capabilities
without a guessed install command. Presence alone is not proof of executable
integrity, version compatibility or permission to trace another process.

The use of `curl` is never automatic; HTTP is task-authorized only. `strace`
may be unavailable in containers even when installed and can expose secrets;
it is diagnostic-only and never executed by this planner.

Source inspirations: [`voku/dotfiles` first-install concept](https://github.com/voku/dotfiles/blob/master/firstInstallDebianBased.sh)
and [`awesome-ai-friendly-cli`](https://github.com/alies-dev/awesome-ai-friendly-cli).
Do not inherit historical dotfiles global shell changes or quiet-output claims.

## Future gates

A separate approved slice may add an **explicit** install/apply mode only after
isolated Ubuntu/macOS dogfood and package-source/permission review. The fixed
`.redpill/` shell runtime is packaged separately by `install.sh`; it is not a
planner profile and never installs tools.
No automatic install is authorized by this document.
