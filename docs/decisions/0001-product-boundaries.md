# ADR 0001: Separate runtime payload from maintainer tooling

- Status: Accepted as a boundary; physical directory migration pending; Superseded in part by [ADR 0003](0003-shell-only.md)
- Date: 2026-10-12
- Context: [Redpill-inspired environment RFC #40](https://github.com/voku/agent-dotfiles/issues/40)

## Decision

One owner per file. The only consumer payload is the allowlisted private-prefix runtime in `tools/install.py`; everything else stays in the source checkout. No implicit `$HOME` deployment, global host mutation or sourced upstream interactive configuration. Diagnostic `profiles/*.json` remain data-only; the uninstalled `examples/gitconfig.agent.example` is an example and must not be mistaken for an activation layer.

Do not add generic dotfile managers, redundant tool runners or an alias framework merely to change the directory tree. Rename/move owners in independently verifiable slices, updating the fixed installer allowlist, shell activation and actual consumer tests atomically.

## Tradeoffs

The current checkout remains visually mixed temporarily. In exchange, an existing consumer cannot silently change runtime behavior because a maintainer renamed a directory. A future directory migration needs an explicit before/after pinned manifest comparison and real Bash/Zsh and cold-install evidence.

## Consequences

The documentation must show what is installed, what is only a diagnostic, and what belongs to this repository's own maintenance. Agent-specific command defaults should be opt-in, scoped and independently evaluated before promotion.
