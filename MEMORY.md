# Repository memory

This is reviewed, versioned knowledge for **voku/agent-dotfiles**, not a transcript or a substitute for tests. An agent changing behavior must verify the named canonical source and update this index only when the lesson is durable. Unreviewed task state and private context do not belong here.

| Subject | Durable rule | Canonical source |
| --- | --- | --- |
| Deployment | No automatic writes to `$HOME`, login files or global Git configuration. Runtime activation is explicit and installs into an approved private prefix. | `tools/install.py`, `shell/core/activation.sh`, installation tests |
| Project versus consumer | Diagnostic JSON profiles are not shell config. `tools/`, `tests/`, `.github/` and this memory are repository-owned, not consumer payload. | `tools/install.py::installation_path`, `docs/REPOSITORY_LAYOUT.md` |
| Output honesty | A bounded search or patch must preserve error statuses, source identity and truncation; never replace necessary source with a diffstat to reduce text. | `agent_dotfiles/cli.py`, `tests/test_context_quality.py` |
| Shell lifecycle | Both Bash and Zsh explicitly source fixed reviewed modules and refuse collisions/missing assets rather than silently falling back to host functions. | `shell/core/activation.sh`, `tests/test_shell_profiles.py` |
| Workflow authority | `agent-loop` owns workflow approvals, Learning decisions and host orchestration. This repository can retain only its reviewed project-local rules/decisions/findings. | `docs/AGENT_LOOP.md`, `docs/decisions/0002-repository-learning.md` |
| Evidence gate | Do not claim general speed or token improvements from green unit tests, output byte counts or historical comparisons with confounders. Until a real controlled agent trial passes, no default routing. | `docs/EVALUATION_2026-10-11.md`, [evaluation #12](https://github.com/voku/agent-dotfiles/issues/12) |

Decisions are in [docs/decisions](docs/decisions/0001-product-boundaries.md); the exact repository/consumer path inventory is [docs/REPOSITORY_LAYOUT.md](docs/REPOSITORY_LAYOUT.md). Facts recorded for repository state on 2026-10-12 must be rechecked against the current code after each relevant change.
