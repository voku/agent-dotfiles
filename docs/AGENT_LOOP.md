# Integration boundary: agent-loop

Source issue: https://github.com/voku/agent-loop/issues/756

`agent-loop` already owns tool inventory (`src/Init/InitToolsCommand.php`), navigation and mapped PHP symbol discovery (`agent-loop-investigate`), and workflow governance. **Do not duplicate that authority here.**

`agent-dotfiles` exposes optional, read-only CLI helpers. It does not patch agent-loop hooks, ban grep/find itself, decide whether to use Map, or install skills in external repositories. Initial integration is manual and opt-in: invoke this tool by its path when a bounded literal/file-search experiment benefits from it.

Before integration: compare against direct `rg --json`, `rg --files -0`, `git ls-files -z` and `agent-loop map` using repeated tasks; verify actual output and costs. Only update `agent-loop` after a measurable benefit. Track changes separately in the owner repository.
