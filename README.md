# agent-dotfiles

**Shell dotfiles for coding agents (LLMs), in the layout of
[voku/dotfiles](https://github.com/voku/dotfiles).**

The source dotfiles are written by a human for a human at an interactive prompt.
This repository is the same idea for a non-interactive agent shell: the familiar
`.exports`, `.functions` and `.redpill/` files, but with session settings and
helpers that keep tool output plain, bounded by the tool and complete.

Nothing is installed, copied to `$HOME`, or loaded automatically. You source one
reviewed file in a shell you control, and `agent_deactivate` removes it again.

```sh
env -u BASH_ENV bash --noprofile --norc      # or: zsh -f
source /absolute/path/to/agent-dotfiles/.bashrc   # .zshrc in Zsh
agent_git -C /project status --short
agent_rg -n -F -- 'function save(' /project
agent_deactivate
```

## Layout

| Path | Role |
| --- | --- |
| `.bashrc`, `.zshrc`, `.shellrc` | Explicit entry points; resolve the checkout root and activate |
| `.exports` | `AGENT_DOTFILES_HOME`; applies the CLI settings in `.redpill/config/agent.env` |
| `.functions` | `agent_*` helpers: Git/rg wrappers, `agent_require`, `agent_head`, `agent_os`, `agent_php_lint`, `agent_extract`, ... ([list](docs/SHELL.md)) |
| `.redpill/lib/` | Activation preflight and `agent_deactivate` |
| `.redpill/config/` | Tool configuration files (`agent.env`, `ripgreprc`, opt-in `gitignore_global`) |
| `tests/shell/` | Bashunit contracts run against real Bash and Zsh |
| `docs/` | [Shell contract](docs/SHELL.md), [layout](docs/REPOSITORY_LAYOUT.md), [agent-loop boundary](docs/AGENT_LOOP.md), [decisions](docs/decisions/) |

No progress bars, color, pagers, update nags or prompts: `agent.env` sets the
per-tool variables (Git, Composer, npm, pip, Cargo, ...) only where the host has
not, and deactivation removes exactly those. See [docs/SHELL.md](docs/SHELL.md) for the full
list and how to add one.

## Skills

Skills live in [voku/agent-skills](https://github.com/voku/agent-skills), including
`coding-simplicity`, `testing-best-practices`, `php-static-analysis`,
`language-onboarding-authoring` and `project-onboarding`. This repository ships none.

## Boundaries

No startup-file edits, package installs, login-shell changes, global Git
configuration, daemons, or command shadowing. Task workflow, approvals,
Learning, Recall and memory belong to [agent-loop](docs/AGENT_LOOP.md).

## Validate

```sh
bashunit test tests/shell --strict
```

MIT licensed; see [CONTRIBUTING](CONTRIBUTING.md), [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md)
and [SUPPORT](SUPPORT.md). Origin: [UPSTREAM.md](UPSTREAM.md).
