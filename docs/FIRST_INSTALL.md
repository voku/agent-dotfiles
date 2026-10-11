# First install: developer tool capability plan (S0)

The current `firstInstall.sh` is **read-only**. It detects binaries and supported
platform package managers and prints one JSON recommendation. It does not
execute a package manager, install tools, change HOME or global Git, or contact
the network. Installation of the agent-dotfiles runtime is separately handled by
[`install.sh`](INSTALLATION.md), using reviewed full Git commits.

```sh
./firstInstall.sh plan
./firstInstall.sh plan --profile php
./firstInstall.sh plan --profile debug
```

Profiles are fixed inventories, not shell startup scripts:

- `minimal`: Python 3, Git, ripgrep, jq, curl.
- `php`: minimal plus PHP and Composer (detected only: no assumed correct system PHP packages).
- `debug`: minimal plus fd/fdfind, ShellCheck, hyperfine and Linux-only strace.

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
isolated Ubuntu/macOS dogfood and package-source/permission review. Another
slice may add fixed `.redpill/` profiles with backwards-compatible manifests.
No automatic install is authorized by this document.
