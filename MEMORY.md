# Repository memory

Short, reviewed project knowledge for `voku/agent-dotfiles` maintainers using
agent-loop. Raw observations, sessions and Recall receipts stay in local,
untracked `.agent-loop/`.

| Subject | Durable rule | Canonical home |
| --- | --- | --- |
| Scope | Shell-only: `.exports`, `.functions`, `.redpill/` and Bash/Zsh entry points. No Python CLI, installer, profiles or bundled skills. | `docs/decisions/0003-shell-only.md` |
| Skills | Owned by `voku/agent-skills`; never vendor copies here. | `docs/REPOSITORY_LAYOUT.md` |
| Activation | Explicit sourcing only; refuse on missing asset or name collision; set an env default only if the host has not; `agent_deactivate` removes exactly what was added. | `.redpill/lib/`, `.exports`, `tests/shell/activation_test.sh` |
| Helpers | One `agent_*() {` per helper in `.functions`; the owned namespace is derived from it. Helpers are read-only or write only to an explicit destination, never page, color or truncate silently (`agent_head` announces cuts). | `.functions`, `docs/SHELL.md` |
| CLI settings | `.redpill/config/agent.env` removes noise (progress, color, pagers, prompts) only; never CI=true, quiet/audit switches or anything that hides results. | `.redpill/config/agent.env`, `docs/SHELL.md` |
| Evaluation claims | A green CI run does not prove better agent outcomes; claims need the controlled comparison in issue #12. | issue #12 |
