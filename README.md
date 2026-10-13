# agent-dotfiles

**A comfortable, native-first workspace for coding agents.**

Agents already know `git`, `rg`, `sed`, `find`, shells and project test tools.
This repository prepares those tools and the environment around them. It does
not teach agents a second command language.

The layout takes inspiration from [voku/dotfiles](https://github.com/voku/dotfiles).
Its practical navigation and repository shortcuts are adapted here as a few
non-interactive Bash/Zsh functions that keep native commands available.

## Fresh Debian or Ubuntu setup

From a reviewed, clean, committed checkout, preview the setup with a private
prefix and the exact full commit:

```sh
mkdir -p "$HOME/.local/opt"
./bootstrap.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
```

This is read-only. Review the package plan, then repeat the command with
`--apply` to install the fixed Debian/Ubuntu package allowlist and pinned shell
payload. On a bare Debian/Ubuntu host without Python 3.10+, the first `--apply`
only installs Python 3 and prints the complete plan; review it, then run
`--apply` again. Applying other package changes requires root or noninteractive
`sudo`. The bootstrap does not edit startup files, change login shells, or
write global Git settings.

For the same task environment in Bash or Zsh, source one reviewed entry point:

```sh
. "$HOME/.local/opt/agent-dotfiles/activate.sh"
```

It loads the correct explicit profile, applies session-only Git defaults and
provides `agent_deactivate` to restore the prior Git environment and remove the
shell namespace. It is safe to source twice. In fresh per-command Bash sessions,
use `env -u BASH_ENV bash --noprofile --norc`; in Zsh, use `zsh -f`. The setup
never writes these into startup files.

## Native workflow

```sh
git status --short --branch
rg -n --hidden --glob '!vendor/**' 'target symbol' src tests
sed -n '40,100p' src/path/to/file.php
git diff -- src/path/to/file.php
./vendor/bin/phpunit --filter RelevantTest
```

Use native output as-is. Search and inspect the relevant source before editing;
run the project's own focused checks; inspect the full diff and visible errors.
The shell environment does not cap output, rewrite commands, or claim shorter
output as a quality improvement.

The explicitly activated shell also provides a few small Bash/Zsh comforts:

- `agent_context` prints the repository root, full short status, and staged and
  unstaged diff summaries. In Composer projects it also reports declared PHP
  requirements, script commands, common project config files, and available
  PHP/Composer/check executables. It only reads this information; it does not
  run scripts or install dependencies. Read source and full patches before
  making decisions.
- `agent_root` moves to the repository root.
- `agent_diff [PATH...]` shows the complete native patch with external diff
  drivers and text conversion disabled.
- `agent_diff_check` checks staged and unstaged whitespace errors.
- `agent_mkcd DIRECTORY` creates a directory and enters it.

These functions are optional conveniences loaded by `activate.sh`. Direct
`git`, `rg`, shell and project commands remain fully available.

Git defaults in `git-env.sh` are additive and session scoped: pager `cat`, color
off, histogram diff, rename detection and ISO strict log dates. Histogram only
changes diff presentation. Patches and error messages remain complete. The
reviewable native config reference is [.gitconfig](.gitconfig); no file is
copied into global Git configuration. Deactivation checks that the owned Git
environment slots are unchanged before restoring the inherited state.

The default Debian/Ubuntu package plan includes `fd`/`fdfind`, ShellCheck,
hyperfine and Linux `strace` alongside the core tools. These remain ordinary
optional native tools; agent-dotfiles adds no command wrappers for them.

Users of the removed Python consumer CLI can follow the short
[native-command migration note](docs/MIGRATION_FROM_PYTHON_CLI.md).

## Contents

- `activate.sh`, `.bashrc`, `.zshrc` and `.redpill/`: one explicit Bash/Zsh
  activation path with no
  prompt framework, plugin discovery or user profile loading.
- `bootstrap.sh`, `firstInstall.sh` and `install.sh`: host setup, capability
  planning and pinned private-prefix installation.
- `git-env.sh`: session-only Git defaults.
- `skills/`: reviewed, opt-in agent guidance.
- `tools/`: maintainer-side installer, provenance and release utilities.

The secure manifest installer and maintainer automation still use Python
internally. Python is no longer a coding-agent runtime or consumer command.

See [setup details](docs/FIRST_INSTALL.md), [installation](docs/INSTALLATION.md),
[repository layout](docs/REPOSITORY_LAYOUT.md), and [agent-loop boundary](docs/AGENT_LOOP.md).
This project provides an environment; agent-loop remains the independently
installed task workflow.
