# Pinned installation

`install.sh` copies a reviewed, full-commit-pinned checkout into an explicit
private prefix. It verifies the installed files against a SHA-256 manifest and
supports verification and uninstall. It never edits user startup files or
global Git configuration.

For a fresh Debian/Ubuntu host, prefer the single setup entry point:

```sh
mkdir -p "$HOME/.local/opt"
./bootstrap.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
```

The checkout must be clean and at the exact supplied commit. For a host that
already has its tools, install only the reviewed dotfiles and opt-in skills:

```sh
./install.sh plan --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
./install.sh --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
./install.sh verify --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
```

The installer implementation uses Python 3.10+ internally for safe path
handling, immutable commit reads and manifest verification. Consumers do not
receive a Python command-line tool. Uninstall only a prefix whose manifest
verifies:

```sh
./install.sh uninstall --prefix "$HOME/.local/opt/agent-dotfiles" --revision FULL_COMMIT_SHA
```

Activate the same shell and Git defaults in Bash or Zsh with one entry point:

```sh
. "$HOME/.local/opt/agent-dotfiles/activate.sh"
agent_deactivate
```

The entry point selects the appropriate shell profile, appends scoped Git
settings, and restores the prior environment when deactivated. It does not
replace or edit global, system or repository config.
