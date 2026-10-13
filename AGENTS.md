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

<!-- agent-loop:project-instructions:begin -->
## agent-loop workflow router

This repository uses `voku/agent-loop` for governed coding work. Keep this always-on router small; detailed procedures live in the installed skills and CLI help. If host integration is uncertain, run `vendor/bin/agent-loop init host-status --format=json` and obey its `next_action_kind` / `next_action` until no repository-owned action remains; `runtime_boundary` describes host/user scope and is not authority to mutate it. Troubleshooting only: use `vendor/bin/agent-loop init status` to inspect broader setup and `init sync-instructions` when managed instruction projection itself needs repair.

Before the lifecycle CLI is runnable, recover only the minimum reversible workspace/tool bootstrap needed to execute the repository's declared workflow: inspect the checkout/remotes, fetch the obvious public repository, install already-declared Composer dependencies, obtain required public sibling checkouts for cross-package work, discover available host/GitHub capabilities without exposing credentials, and establish an isolated branch or worktree before implementation. This bootstrap is not product-code mutation and does not authorize approval, task state, or owner artifacts. Missing `vendor/`, a missing remote, or an unavailable preferred PR/push tool is not by itself a terminal workflow blocker; continue safe local work until the next genuinely required action cannot be performed.

For a durable task id:

1. Before mutating product code, run `vendor/bin/agent-loop enter <task-id> --format=json` and obey the returned `next_action_kind` / `next_action`. `command` means execute it as written; `command_template` means fill model-owned placeholders from the actual request and repository evidence and execute it without asking a human merely because placeholders exist; `decision_required` means a genuine human-authority decision is required, so show the exact current decision subject before asking; `host_work` means perform the described host-native implementation/model work; `none` means there is no further lifecycle action. Never fabricate an approval or risk owner.
2. Use matching repository skills/subagents; a router may select a specialist but never a lifecycle phase. Only the current result routes task start/progress, Recall/L2, repair, Learning, review, or close. Do not recreate procedures from chat: do not pre-build Map/Search, create Session/Recall state, or infer approval/close ordering.
3. When host-native mutation is complete, run `vendor/bin/agent-loop finish <task-id> --format=json`, then obey its canonical next step until `next_action_kind=none` and the result is complete. If a human decision is requested, present the exact Contract/review/Learning/risk evidence being decided instead of asking for a generic confirmation. If an advertised command deterministically refuses without changing the next step, report a workflow defect rather than teaching the host a private workaround.
4. Never claim that hooks fired, checks passed, CI is green, a PR merged, or a release/deploy shipped unless current evidence proves it.

For untracked exploration, use an ephemeral session rather than inventing a durable task.

### Agent Learning

This project uses `voku/agent-learning` for reviewable evidence and durable guidance.
- Durable findings, proposals, and LearningNotes live below `.agent-loop/learning/`.
- Record validated findings or LearningNotes using the canonical learning commands/skills (`agent-learning-consumer`, `agent-learning-note`).
- Never auto-promote unverified findings, raw LLM observations, or dream output into active guidance.
<!-- agent-loop:project-instructions:end -->
