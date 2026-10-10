# Explicit, pinned installation and rollback

The CLI and namespaced Bash/Zsh profiles are optional. They never modify
user shell startup files, PATH, global Git config, hooks, prompts or agent-loop.

## Install and verify

Use a trusted, clean Git checkout at an **independently approved full
40-character SHA**. Do not automatically substitute a dynamic HEAD for an
approved revision. The destination must have an existing private parent,
be outside the checkout, and be absent or empty. No symlink ancestors, `..`
path traversal or dirty tracked runtime files are allowed.

```bash
./install.sh install --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-approved
./install.sh verify --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-approved
```

The root script always installs from its own checkout and refuses a supplied
`--source`. For direct use, `python3 tools/install.py install --source
CHECKOUT --revision SHA --prefix PREFIX` remains available. The installer
compares tracked runtime files against Git objects, stages beside the prefix,
and verifies before atomic rename. It installs only the Python package,
the original executable, the LICENSE, and the three shell profile files,
plus a generated launcher and a SHA-256/mode manifest. Nothing is downloaded.

## Explicit shell activation

In a **fresh** Bash consumer session:

```bash
source /private/existing-parent/agent-dotfiles-approved/shell/.bashrc
agent_doctor
agent_files --root . --limit 30
agent_history 5
agent_blame src/File.php 10 25
```

In fresh Zsh use the same prefix's `shell/.zshrc`. Do not source it in
`~/.zshrc` or `~/.bashrc`. Profiles refuse function collisions and a different
active pin; helpers never override native Git or ripgrep commands.
`agent_doctor` returns capability inventory, or fails under `--strict`.
Missing optional capabilities are not grounds for changing Loop policy.

The JSON installer schema is `agent-dotfiles.v1.installation`. Exit 0 is
success; exit 2 is an explicit error/refusal. CLI navigation retains its
documented 0/1/2/3 codes. Source/output and manifest are not a digital
signature: verify the trusted Git provenance separately.

## Remove or roll back

Stop consumers before removal. Preserve old approved prefixes. Rollback
means starting a **new** consumer shell with the old prefix.

```bash
./install.sh uninstall --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-approved
```

Removal verifies **all** installed paths and modes, including shell files,
and refuses modified/extra/missing content or symlink entries. No forced
removal exists. Use the installer corresponding to that version's manifest.
Concurrent hostile filesystem mutation and compromised trusted checkouts
are not covered by this private-prefix threat model.

macOS needs canonical paths (`/private/var`, not symlinked `/var`).
Windows is outside this installation contract.
