# Agent-owned Bash and Zsh setup

These dotfiles share the familiar layout of `voku/dotfiles`, but their contents
are independently designed for agents. They do not source upstream/user profiles,
load `.redpill`, create terminal sessions, configure prompts or change shell options.
No helper shadows `git`, `rg`, `cd` or another native command.

## Explicit activation

Use a reviewed checkout for development or a verified, full-commit-pinned private
prefix for a fresh consumer. [Installation](INSTALLATION.md) explains verification.

```bash
# Bash
source /absolute/agent-dotfiles/.bashrc
# Zsh (use this instead in a Zsh shell)
source /absolute/agent-dotfiles/.zshrc
```

For hosts that run each tool call in a new shell, activate in that call explicitly:

```sh
bash --noprofile --norc -c '. "$1/.bashrc"; shift; agent_search "$@"' \
  consumer /absolute/agent-dotfiles 'function save(' --root /project --glob '*.php'
```

Activation is silent on success. It exports `AGENT_DOTFILES_HOME` and defines only
the functions below. PATH, working directory, positional arguments and shell options
are preserved. Shared files are resolved beside the selected profile, never from
HOME or the project being investigated. Use `bash --noprofile --norc` or `zsh -f`
when creating a dedicated shell; activation itself cannot undo an already-loaded
user configuration. Source `.bashrc` in Bash and `.zshrc` in Zsh, not via `sh`.

Activation refuses existing owned names or `AGENT_DOTFILES_HOME` rather than
replacing custom definitions. Run `agent_deactivate` before activating another
version. No eval-based restoration or command interception is involved.

## Helpers

All helpers preserve argument boundaries, stdout, stderr and exit status. The
context helpers produce exactly the standalone CLI's JSON, limits and errors.
Use `--help` on a helper for the corresponding CLI contract.

| Helper | Operation |
| --- | --- |
| `agent_dotfiles` | Invoke any standalone CLI subcommand |
| `agent_doctor` | Actual executable capability inventory |
| `agent_files` | Ignore-aware file discovery |
| `agent_search` | Literal search by default; explicit regex/glob/path options |
| `agent_read` | Exact source ranges and whole-file hash |
| `agent_tracked` | NUL-safe tracked inventory |
| `agent_status` | Individual worktree paths, including untracked files |
| `agent_patch` | Complete patch for one literal tracked file |
| `agent_history` | Native Git log, with literal pathspecs and no pager/color |
| `agent_blame` | Native Git line-porcelain blame, with literal pathspecs |
| `agent_deactivate` | Remove this namespace and installation-location export |

```bash
agent_files --root /project --hidden --limit 100
agent_search 'invoice.total' --root /project --path templates --glob '*.twig'
agent_read 'src/name [v2].php' --root /project --start 20 --end 70
agent_tracked --root /project
agent_status --root /project
agent_patch 'src/name [v2].php' --root /project
(cd /project && agent_history -- src/Service.php)
(cd /project && agent_blame -- src/Service.php)
```

Native history/blame use Git's own syntax and output, not JSON envelopes or the
CLI's output caps. History/blame operate in the current repository; their arguments are passed to
`git log` and `git blame`, respectively. Use a subshell as above for another root.
Read the complete patch or source when required; bounded discovery never proves
that omitted context is irrelevant. Exit 3 signals incomplete discovery, exit 1
means a completed search found no matches, and exit 2 means a CLI error.
Untracked/ignored files need explicit `agent_read` evidence; they cannot supply
tracked patch evidence. Structural PHP questions remain owned by agent-map and
agent-loop's investigation workflow.

## Rollback

Run `agent_deactivate` or exit the dedicated shell. Activate the previous verified
prefix in the next fresh consumer; never replace a running session's toolset.
The installer never modifies HOME startup files, so uninstall needs no global
configuration restoration. Optional tools cannot prevent agent-loop from starting.
