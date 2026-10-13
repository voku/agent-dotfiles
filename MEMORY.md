# Repository memory

Short, reviewed project knowledge for `voku/agent-dotfiles` maintainers using
agent-loop. Raw observations, sessions and Recall receipts stay in local,
untracked `.agent-loop/`.

| Subject | Durable rule | Canonical home |
| --- | --- | --- |
| Scope | Shell-only: `.exports`, `.functions`, `.redpill/` and Bash/Zsh entry points. No Python CLI, installer, profiles or bundled skills. | `docs/decisions/0003-shell-only.md` |
| Skills | Owned by `voku/agent-skills`; never vendor copies here. | `docs/REPOSITORY_LAYOUT.md` |
| Activation | Explicit sourcing only; refuse on missing asset or name collision; set an env default only if the host has not; `agent_deactivate` removes exactly what was added. | `.redpill/lib/`, `.exports`, `tests/shell/activation_test.sh` |
| Helpers | `agent_git`, `agent_rg`, `agent_diff`: the native command with host-config bleed removed, nothing more. One named exception, `agent_head` (announced truncation; failure mode observed in 6,148 of 12,121 calls, outcome benefit unproven). Task strategy (search choice, completeness, linting, orientation, archives) is guidance for agent-skills. `agent_rg` is not a completeness tool (#70). A new or reinstated helper needs its own failure mode and task evidence. | `docs/decisions/0004-environment-vs-task-strategy.md`, `.functions` |
| CLI settings | `.redpill/config/agent.env` removes noise (progress, color, pagers, prompts) only; never CI=true, quiet/audit switches or anything that hides results. | `.redpill/config/agent.env`, `docs/SHELL.md` |
| Evaluation claims | A green CI run does not prove better agent outcomes; claims need the controlled comparison in issue #12. | issue #12 |
