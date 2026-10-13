# ADR 0002: Native tools are the agent interface

- Status: Accepted
- Date: 2026-10-12
- Context: Coding agents already use Git, rg, shell and project-native tools.

## Decision

Remove the Python consumer CLI and its command wrappers. Prepare an explicitly
activated Bash/Zsh environment, session-scoped native Git defaults and opt-in
skills. Do not make agents learn `agent-dotfiles search`, `read`, `workspace` or
similar commands.

Keep Python only inside pinned installation and maintainer tooling where it
provides path safety, immutable commit reads and manifest verification. This
internal use is not exposed as an agent runtime.

## Consequences

Agents work with native output and complete errors and patches. The project
accepts losing structured JSON envelopes and wrapper-specific bounds. Setup
correctness and comfort must be judged in real coding sessions before adding
new abstractions. No global Git configuration or automatic shell activation is
introduced.
