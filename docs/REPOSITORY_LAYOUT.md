# Repository layout

Everything here is either an explicitly sourced shell file or maintenance
material. Nothing is copied to `$HOME`.

| Path | Owner | Notes |
| --- | --- | --- |
| `.bashrc`, `.zshrc`, `.shellrc` | Shell environment | Entry points; never read user startup files |
| `.exports`, `.functions` | Shell environment | Settings and helpers, named as in `voku/dotfiles` |
| `.redpill/lib/`, `.redpill/config/` | Shell environment | Activation lifecycle; tool configuration files |
| `tests/shell/`, `.github/` | Maintainers | Bashunit contracts and CI |
| `docs/`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md` | Maintainers | Source references only |
| `MEMORY.md`, `docs/decisions/` | agent-loop (maintainer use) | Reviewed project knowledge; raw `.agent-loop/` stays untracked |

Skills belong to [voku/agent-skills](https://github.com/voku/agent-skills).
Task workflow, Learning, Recall and memory belong to agent-loop.

There is no `.aliases` (aliases do not expand in non-interactive shells), no
Python CLI, no installer and no capability profiles; see
[ADR 0003](decisions/0003-shell-only.md).

Add new tool configuration as a file under `.redpill/config/` selected by that
tool's own environment variable in `.exports`, and keep it presentation-only.
