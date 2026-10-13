# Coding-agent working agreement

Scope: this repository only. The project is an optional, non-interactive
shell profile, not an authority source for `agent-loop` workflows.

## Safe defaults

- Never source user/upstream interactive Bash/Zsh profiles or plugins.
  The reviewed agent-owned profiles here may be explicitly activated in a fresh
  consumer shell; never install them into user startup files automatically.
- Never install binaries, change login shells, alter global Git configuration,
  or launch background daemons.
- Environment defaults in `.exports` must be skipped when the host already set
  the variable and be removed by `agent_deactivate`. Settings change
  presentation or interactivity only; never hide or truncate evidence.
- Prefer small, explainable additions over a universal tool-manager framework.
- Test missing assets, name collisions, unusual paths, and Bash and Zsh.

## Validation

```sh
bashunit test tests/shell --strict   # Bashunit 0.50.1; needs bash, zsh, git, rg
```

Do not infer that all machines or coding hosts share the local PATH. Updating
agent-loop instruction or policy files belongs to agent-loop and requires its
own review.

## Responsibility boundary

`agent-dotfiles` owns only the explicit shell execution environment. Skills,
including `project-onboarding`, are owned by `voku/agent-skills`.
`agent-loop` is an independently selected, separately installed workflow owner
for planning, sessions, review, Learning, Recall and memory. `MEMORY.md` and
`docs/decisions/` are this project's reviewed inputs to that owner; raw
`.agent-loop/` sessions, receipts and findings are local state and remain
untracked. Do not create a second memory format, promote Learning findings, or
modify Loop policy as part of an environment change. See
[repository layout](docs/REPOSITORY_LAYOUT.md) and
[agent-loop integration](docs/AGENT_LOOP.md).

Before recommending any default activation, use the controlled real-task
evaluation owned by [#12](https://github.com/voku/agent-dotfiles/issues/12).
Correctness and complete evidence outrank output-byte reductions.
