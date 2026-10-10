# Changelog

## 0.2.0 - Context-first navigation

- Added exact, source-digest-bound `read` and full-fidelity `git-patch` commands.
- Added NUL-safe Git tracked-files inventory (`tracked`).
- Added scoped search via `--path`/`--glob`; removed `rg --max-columns-preview` to avoid silent line loss.
- Prevented user ripgrep configuration from changing wrapper semantics.
- Added opt-in, project-scoped read-only Git aliases and evidence-first/context policy documentation.
- Expanded optional tool discovery (`ast-grep`, `ctags`, `difft`, `delta`); no automatic installation or hook interception.
- Added security, context, unusual-filename, rename and real-Git integration tests.


## 0.1.0 - Initial bootstrap

- Added non-interactive, read-only `doctor`, `files`, `search` and `git-status`.
- Added bounded, machine-readable JSON output and explicit truncation status.
- Added optional `fd`/`fdfind` detection without using the interactive shell.
- Added first-party executable contract tests and CI matrix.
- Documented upstream dotfiles provenance and separation from `agent-loop`.

No release tag has been created. No GitHub repository has been published yet.

## Unreleased bootstrap

- Import the v0.2.0 candidate with original GitHub LICENSE preserved.
- Add pinned Bashunit integration tests for source fidelity, Git evidence and executable status codes, alongside the existing Python contracts.
- Remove obsolete repository-creation helper now that voku/agent-dotfiles exists.
