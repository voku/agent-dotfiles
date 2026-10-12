# Coding-agent working agreement

Scope: this repository only. The project is an optional, non-interactive
CLI profile, not an authority source for `agent-loop` workflows.

## Safe defaults

- Never source user/upstream interactive Bash/Zsh profiles or `.redpill` plugins.
  The reviewed agent-owned profiles here may be explicitly activated in a fresh
  consumer shell; never install them into user startup files automatically.
- Never install binaries, change login shells, alter global Git configuration,
  or launch background daemons from the CLI.
- Keep filesystem and search commands read-only; invoke external binaries with
  argument lists (`shell=False`).
- Prefer small, explainable additions over a universal tool-manager framework.
- Preserve documented JSON schemas and exit codes; never report truncated
  results as exhaustive searches.
- Test missing tool, unusual filenames, no match, tool errors and bounded output.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q agent_dotfiles bin tests
```

Use `./bin/agent-dotfiles doctor` to report local capabilities. Do not infer
that all machines or coding hosts share the local PATH. Updating agent-loop
instruction or policy files belongs to agent-loop and requires its own review.

- For shell/CLI integration changes run `bashunit test tests/shell --strict` (Bashunit 0.50.1) alongside the Python suite. Bashunit does not replace Python contract tests.

## Project memory and architectural decisions

Read [MEMORY.md](MEMORY.md) and [docs/REPOSITORY_LAYOUT.md](docs/REPOSITORY_LAYOUT.md) before changing activation, profile meaning or install paths. An approved project-specific decision belongs under `docs/decisions/`, not in global agent preferences. This checkout's `.agent-loop/init.json` points at a **project-local** Learning root; do not invent findings or claim a completed Learning/Recall workflow without executing its owner contracts. Review validated Learning records for private data before committing.

Before recommending any automatic alias/default activation, re-run the independent agent task comparison owned by [evaluation #12](https://github.com/voku/agent-dotfiles/issues/12). Correctness and complete evidence outrank fewer bytes of output.
