# CLI reference

`agent-dotfiles` is an optional, read-only CLI. Python 3.10+ and its standard
library implement the JSON interface; `git` and `rg` are used for native source
evidence. It does not install packages or change shell configuration.

Run from a reviewed checkout:

~~~sh
./bin/agent-dotfiles doctor
./bin/agent-dotfiles doctor --strict
./bin/agent-dotfiles files --root . --limit 50
./bin/agent-dotfiles git-status --root . --limit 50
./bin/agent-dotfiles workspace --root . --limit 50
./bin/agent-dotfiles search 'function save(' --root . --glob '*.php' --limit 20
./bin/agent-dotfiles search '^final class ' --root . --regex --limit 20
./bin/agent-dotfiles search 'save(' --root . --path src --glob '*.php'
./bin/agent-dotfiles tracked --root . --limit 100
./bin/agent-dotfiles read src/Service.php --root . --start 80 --end 180
./bin/agent-dotfiles git-patch src/Service.php --root . --base HEAD~1
~~~

These commands are examples; the selected paths must exist. `files` uses
`rg --files --null` by default and supports an explicit `--engine fd` when
installed (with its own semantics). `search` uses `rg --json` and literal
matching by default; opt in to regex, `--hidden`, `--path` or repeatable
`--glob` as the task warrants. Search normally respects `.gitignore`.

## Result and exit contracts

| Exit | Meaning |
| --- | --- |
| `0` | Complete success; `doctor` inventories tools even when some are absent unless `--strict` |
| `1` | Completed search with no matches |
| `2` | Explicit failure: bad arguments, missing tool, process error or strict doctor failure |
| `3` | Truncated or incomplete bounded discovery; narrow scope before drawing conclusions |

Successful commands produce one JSON object on stdout, without a pager or
terminal colors. `read` and `git-patch` refuse to return a partial source or
diff when their exact output cannot fit. Never treat `truncated: true` or exit
`3` as exhaustive evidence.

Stable envelopes: `agent-dotfiles.v1.doctor`,
`agent-dotfiles.v1.files`, `agent-dotfiles.v1.git-status`,
`agent-dotfiles.v1.workspace`, `agent-dotfiles.v1.search`,
`agent-dotfiles.v1.tracked`, `agent-dotfiles.v1.read`,
`agent-dotfiles.v1.git-patch` and `agent-dotfiles.v1.error`.
Limits default to 100 with a maximum of 1000; process output is capped at
2 MiB and wall time at 20 seconds.

## Choose a tool for the question

| Question | Preferred tool |
| --- | --- |
| A literal text/config/template match | Native `rg` or bounded `search` for structured coordinates |
| Discover file paths | `rg --files -0` or bounded `files` |
| Enumerate tracked files | `git ls-files -z` or `tracked` |
| Find worktree changes | `git status --porcelain=v1 -z` or `git-status` |
| Verify checkout root, HEAD and Git state | `workspace`, with explicit incomplete snapshot boundaries |
| Read an exact source range | `read`, including original bytes and whole-file SHA-256 |
| Review an exact path patch | `git-patch`, preserving full-index/binary diff and rejecting truncation |
| Find PHP symbols/callers/impact | Fresh `agent-loop map` / `agent-map` when available |
| Check optional commands | `doctor`, not an assumed PATH |

`workspace` refuses inherited `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE` overrides. It reports the canonical root, HEAD,
branch/detached status and individual bounded porcelain status entries.
HEAD is checked before and after the scan, but the worktree scan is not
atomic. A truncated status must not be interpreted as clean.

`tracked` describes the Git index, not all ignored/untracked files.
`read` preserves original whitespace/newlines, explicit EOF metadata and
whole-file digest. `git-patch` returns an exact selected-file patch, never
substitutes a diffstat. Avoid lossy proxying of Git, tests, PHPStan or other
native output.

## Related documentation

- [Bash/Zsh activation and namespaced functions](SHELL.md)
- [Pinned installation and rollback](INSTALLATION.md)
- [Context selection and completeness](CONTEXT_POLICY.md)
- [Tool selection matrix](TOOL_MATRIX.md)
- [Security contract](SECURITY.md)
