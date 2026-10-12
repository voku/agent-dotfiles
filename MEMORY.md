# Repository memory

This is short, reviewed project knowledge for `voku/agent-dotfiles` maintainers
using agent-loop. It indexes executable and documented truth; raw observations,
sessions, Recall receipts and Learning state belong under local `.agent-loop/`
and are intentionally not committed or installed for consumers.

## Durable repository rules

| Subject | Durable rule | Canonical home |
| --- | --- | --- |
| Consumer boundary | The pinned installer projects only the audited runtime and selected skills. Project documentation, decisions, MEMORY and raw workflow state never enter a consumer prefix. | `tools/install.py`, `tests/test_repository_ownership.py`, `docs/REPOSITORY_LAYOUT.md` |
| Shell runtime | `.redpill/` is the one fixed Bash and Zsh runtime tree. Entry points and fixed loaders may source only reviewed files beneath the selected tool home. | `.shellrc`, `.functions`, `.redpill/`, `tests/test_shell_profiles.py` |
| Agent defaults | Keep deterministic Git and ripgrep settings inside explicit `agent_git` and `agent_rg` calls. Do not override native commands or export global pager, color, PATH or Git settings. | `.aliases`, `docs/SHELL.md` |
| Profiles | `profiles/*.json` is the sole diagnostic capability catalog. It describes `doctor` readiness and never activates shell behavior, installs tools or loads local configuration. | `profiles/`, `agent_dotfiles/cli.py`, `docs/REPOSITORY_LAYOUT.md` |
| Evaluation claims | A green CLI or installation CI run does not prove better coding-agent outcomes. Claims require the held-out, warm-task protocol with agent-loop, model and task conditions held constant. | `docs/STEADY_STATE_EVALUATION.md`, issue #12 |

## Archived task learning

| Archived on | Task | Summary | Archive reason | Durable lesson candidate | Promoted to |
| --- | --- | --- | --- | --- | --- |
| 2026-10-12 | `DOTFILES-52` | Runtime layout and project-memory boundary are being consolidated through a governed change. | The stable rule is recorded above; implementation still needs independent validation and review. | Use a single reviewed runtime tree and keep consumer payload separate from project workflow knowledge. | `MEMORY.md` |
