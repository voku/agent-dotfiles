# agent-dotfiles

**Agent-owned Bash/Zsh dotfiles and an exact-evidence CLI for coding agents.**
Local, explicit, no magic interception. The last release is
[v0.3.0](https://github.com/voku/agent-dotfiles/releases/tag/v0.3.0);
the shell-profile work is unreleased.

## Quick start

Use a clean, reviewed Git checkout and an **independently approved** full
40-character commit SHA. Keep installations in separate private prefixes.

```bash
./install.sh install --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-approved
./install.sh verify --revision APPROVED_FULL_COMMIT_SHA \
  --prefix /private/existing-parent/agent-dotfiles-approved

# In a fresh isolated Bash consumer, never ~/.bashrc:
source /private/existing-parent/agent-dotfiles-approved/shell/.bashrc
agent_doctor
agent_files --root . --limit 30
agent_search 'function save(' --path src --glob '*.php' --limit 20
agent_read src/Service.php --start 40 --end 120
agent_patch src/Service.php --base HEAD~1
agent_history 5
agent_blame src/Service.php 40 60
```

Explicitly source `shell/.zshrc` in a fresh Zsh session instead. You may also
invoke `bin/agent-dotfiles` by absolute path without any shell profile.
`agent_help` lists the function signatures.

## Behavior and limitations

- No user startup edits, PATH updates, global Git config, aliases, hooks,
  user profile sourcing, remote installers or background daemons.
- Fully pinned offline installation, integrity verification and fail-closed
  removal. Rollback means selecting a prior installed prefix in a fresh session.
- Bounded `files`, `search`, `git-status`, `tracked`; exit 3 marks truncated
  navigation. No-truncation `read` and `git-patch` preserve exact source/patch
  bytes and hashes. Errors are explicit.
- Shell functions `agent_doctor`, `agent_files`, `agent_search`,
  `agent_status`, `agent_tracked`, `agent_read`, `agent_patch` forward
  CLI arguments and exit codes unchanged. `agent_history` and `agent_blame`
  use native Git with complete metadata; they do not compress evidence.
- Existing namespaced functions and activation of a different pinned version
  in the same shell are rejected rather than silently overwritten.
- For PHP symbols/callers, use a fresh `agent-loop map`. When optional tooling
  is missing, native Git/ripgrep and existing Loop workflows remain available.

Requires Python 3.10+, Git, Bash or Zsh and ripgrep for source search. The
runtime uses Python's standard library; Linux/macOS are the tested platforms.
Windows installation is not supported.

## Development and testing

```bash
python3 -m compileall -q agent_dotfiles bin tests tools
python3 -m unittest discover -s tests -v
bash -n install.sh shell/.bashrc shell/agent-functions.sh
# If installed:
zsh -n shell/.zshrc shell/agent-functions.sh
bashunit test tests/shell --strict
```

`shell/` owns the opt-in dotfiles; `agent_dotfiles/` owns deterministic
navigation; `install.sh` and `tools/install.py` own installation.
Release tarballs, saved traces and mutation databases are historical evidence,
not live source. [The original v0.3.0 experiment](docs/FULL_CYCLE.md) is
available through commit-pinned references.

Further reading: [installation](docs/INSTALLATION.md),
[security](docs/SECURITY.md), [context policy](docs/CONTEXT_POLICY.md),
[Git provenance](docs/GIT_CONTEXT.md) and
[agent-loop boundary](docs/AGENT_LOOP.md).

## What was actually measured

Four fresh governed agents found a bounded correctness improvement in installed
file reading (4/6 to 6/6 held-out cases). Overall task productivity was
**inconclusive**: no model-token telemetry or general speed advantage was
demonstrated. Native tools remain the default; larger trials belong to
[issue #12](https://github.com/voku/agent-dotfiles/issues/12).
