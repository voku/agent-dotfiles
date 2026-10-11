# Pinned, optional installation

The source checkout works directly with `./bin/agent-dotfiles doctor`; installation
is optional. Agent-loop starts and governs tasks without this tool. Use a separate
prefix for each approved source commit, keeping builder, validator and consumer
environments separate. Never update the toolset inside the session maintaining it.

Requirements: Python 3.10+, Git for installation, and an existing private parent
directory. Runtime capability requirements are reported by `doctor`; Git and
ripgrep supply the normal source-search and Git operations. No package manager,
network installer, shell startup change or global configuration is involved.
The implementation targets Linux and macOS; platform test coverage is determined
by the current CI matrix. Windows is not supported by this installation contract.
On macOS use a canonical parent path (for example `/private/var/...` rather than
the `/var` symlink). Symlink ancestors are refused on every platform.

## Install from an approved checkout

Obtain the checkout through your existing trusted Git access, review the desired
commit and check out that commit yourself. Use its independently approved **full
40-character commit SHA**, not a branch name or a dynamically resolved HEAD as
the approval pin. Run this installer from the reviewed checkout:

```sh
/path/to/agent-dotfiles/install.sh \
  --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-APPROVED_FULL_COMMIT_SHA
```

Replace the capitalized placeholders. The prefix must be absent or empty, outside
the checkout, and without symlinks or `..` components. All tracked checkout files
must be clean; untracked and ignored files are excluded. The installer reads the
pinned Git objects and checks the runtime files against the working copy. It copies
only tracked Python package files, the original entry point, the five agent-owned
shell profiles/shared files, the two fixed `shell/modules/` helper files, the two `shell/core/` lifecycle files and the license, plus
a small generated launcher and a versioned installation manifest. It refuses
tracked runtime symlinks. Installation is staged beside the prefix and renamed
only after validation, leaving an existing installation untouched on failure.

The original entry point is retained as `libexec/agent-dotfiles`. The generated
`bin/agent-dotfiles` imports the isolated package and disables bytecode generation
before imports, so invoking it does not create unmanaged `__pycache__` files.
Files use deterministic modes: launcher `0755`, source files `0644`. The manifest
records the source SHA, SHA-256 file digests and modes; it contains no credentials.

## Activate, diagnose and verify

Activation is explicit: invoke the absolute executable or source the installed
agent-owned profile in a fresh Bash/Zsh consumer. Never source user/upstream
interactive dotfiles or modify user startup files. See [shell setup](SHELL.md).
First verify the approved version and inspect capabilities:

```sh
/path/to/agent-dotfiles/install.sh verify \
  --prefix /private/existing-parent/agent-dotfiles-APPROVED_FULL_COMMIT_SHA \
  --revision APPROVED_FULL_COMMIT_SHA
/private/existing-parent/agent-dotfiles-APPROVED_FULL_COMMIT_SHA/bin/agent-dotfiles doctor
```

`doctor` reports the actual executable inventory; `doctor --strict` returns 2
when required capabilities are missing. Missing optional tools do not affect
agent-loop startup. See [agent-loop's integration boundary](AGENT_LOOP.md) and
[context policy](CONTEXT_POLICY.md) for routing and source-evidence contracts.

Installer subcommands emit JSON schema `agent-dotfiles.v1.installation`: success
has `ok: true`, operation, source revision and file count; failure has `ok: false`
and an error. Exit status 0 means success, 2 means refusal or operational failure.
Argument syntax errors use standard argparse diagnostics and exit status 2.
Verification checks every file, mode, symlink, missing entry and unknown file or
directory. New installations must include both modules and both lifecycle files; partial
lifecycle manifests fail closed. Older pre-core and pre-modular manifests
remain verifiable and safely removable. The optional `--revision` asserts the independently recorded pin.

The manifest is integrity and provenance bookkeeping, **not a digital signature**.
An attacker who can rewrite the installation and manifest can falsify them.
Keep the prefix private, use independently approved Git provenance, and retain
the reviewed source checkout for reinstallation. Installation and removal require
exclusive access to the prefix: concurrent hostile filesystem modifications are
outside this contract. The installer does not authenticate remote Git commits.

## Rollback and uninstall

Roll back by invoking the previous approved prefix in the next fresh consumer
session. No global state needs restoration. To remove a version, stop its consumer
and use the same reviewed installer version:

```sh
/path/to/agent-dotfiles/install.sh uninstall \
  --prefix /private/existing-parent/agent-dotfiles-APPROVED_FULL_COMMIT_SHA \
  --revision APPROVED_FULL_COMMIT_SHA
```

Deactivate the helpers or exit their consumer shell before removal.
Removal validates the manifest and complete tree first. Modified files, missing
files, unknown directories/files and symlinks cause refusal with the entire prefix
preserved. Inspect the error and recover your local changes yourself; there is no
force-removal option. An installation from a future manifest/launcher version
requires its corresponding reviewed installer. This tool installs no third-party
binaries and removes nothing outside the supplied prefix.
