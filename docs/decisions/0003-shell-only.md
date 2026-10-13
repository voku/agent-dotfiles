# ADR 0003: Shell-only environment; skills live in agent-skills

- Status: Accepted; supersedes the Python CLI, installer, profile and bundled-skill parts of ADR 0001 and ADR 0002
- Date: 2026-10-13

## Decision

The repository is the agent counterpart of `voku/dotfiles`: explicit Bash/Zsh
entry points, `.exports`, `.functions` and `.redpill/`. The Python CLI
(`agent_dotfiles/`, `bin/`), `tools/`, the pinned installer, `firstInstall.sh`,
`profiles/` and the vendored `skills/` were removed.

- The CLI wrapped `rg` and `git` while claiming no measured benefit; native
  commands plus `agent_git` / `agent_rg` cover the same evidence.
- Portable skills are owned by `voku/agent-skills`; vendored copies drifted
  (the testing skill's `_template.md` was already stale). `project-onboarding`
  moved there, rewritten to use only native Git and ripgrep.
- `.aliases` was removed; its two functions moved to `.functions`.
- `.redpill/config/agent.env` now carries real per-tool CLI settings, applied by `.exports`. This reverses the earlier
  rule against exporting pager/color settings: they are applied only on
  explicit activation, only when the host has not set them, and are removed by
  `agent_deactivate`. Claims about task benefit still require the controlled
  evaluation in issue #12.

## Consequences

Consumers use a reviewed checkout directly. There is no pinned-prefix install,
manifest or JSON diagnostics; use `command -v` for capability checks. Older
revisions remain available in Git history.
