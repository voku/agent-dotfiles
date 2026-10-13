# ADR 0002: Fixed Redpill runtime and project memory

- Status: Accepted; Superseded in part by [ADR 0003](0003-shell-only.md)
- Date: 2026-10-12
- Context: [Redpill-inspired environment RFC #40](https://github.com/voku/agent-dotfiles/issues/40)

## Decision

The familiar dotfile entry points remain at the repository root, but their
implementation lives in one fixed `.redpill/` tree. `.functions` loads the
reviewed modules in a declared order. `.aliases` is retained as a recognizable
entry point but exposes named functions, because ordinary aliases are not a
reliable interface for non-interactive coding-agent shells.

`agent_git` and `agent_rg` are optional command-scoped defaults. They preserve
full stdout, stderr and exit status while disabling only the pager, credential
prompt, color and inherited ripgrep configuration relevant to the invocation.
They never shadow native commands or alter global environment settings.

`MEMORY.md` and this decision directory are versioned input for agent-loop when
maintaining this repository. They are not a second workflow implementation and
are excluded from every installed consumer prefix. Raw `.agent-loop/` state
remains local and ignored.

## Consequences

New pinned installations contain the complete root entrypoint set and the
complete `.redpill/` tree. Existing legacy manifests remain verifiable and
removable. Profiles retain one purpose: diagnostics. Any claimed task-quality
benefit still needs the controlled evaluation in issue #12.
