# Agent CLI tool matrix

A tool appearing in dotfiles does **not** prove it is agent-safe. Test actual executable behavior rather than copying aliases.

| Tool | Goal | Usage/contract | Policy |
| --- | --- | --- | --- |
| `rg` | Literal, file search | `rg --json -F -- PATTERN .`, `rg --files -0` | Required for search wrapper |
| `git` | Version-control evidence | `git status --porcelain=v1 -z`, `git ls-files -z` | Required for normal coding workflow, detected only |
| `jq` | JSON processing | `jq -c FILTER FILE`; validate with `jq empty FILE` | Optional, prefer no display decoration |
| `php` | PHP project inspection and native checks | Discover interpreter before selecting project commands | Required only for `doctor --profile php` readiness |
| `composer` | PHP dependency/project metadata | Use only after inspecting the project and its declared commands | Optional within PHP profile; executable presence is not compatibility |
| `fd` or `fdfind` | Alternate file search | `fd --type f --print0` | Optional, **explicit selection**, no silent semantic fallback |
| `shellcheck` | Shell diagnostics | File-scoped invocation | Optional, gate before CI use |
| `strace` | Linux syscall evidence | Small, scoped target; sanitize sensitive traces | Optional, never always-on |
| `hyperfine` | Command performance evidence | Repeat runs, record machine + cache state | Optional, benchmark harness later |
| `fzf` | Interactive terminal selection | TTY and key binding assumptions | Excluded from agent profile |
| `ag` with pager | Human readable text search | Can invoke `less` or add color | Excluded from agent profile |
| `.redpill` functions | Namespaced, noninteractive agent commands | Hidden plugins, command replacement, global startup | Fixed reviewed runtime only |

## Differences that matter

- Shell `fd()` and executable `fd` are different objects. Python uses explicit executable paths, no shell resolution.
- `rg --files`, `fd` and `git ls-files` have different inclusion, ignore and tracking semantics. Choose deliberately.
- Colors, pagers, terminal width, timestamps and current shell function tables must not affect machine output.
- Filenames may contain spaces or newlines: use NUL separators internally; JSON path strings encode newlines, and non-UTF-8 paths are represented as Base64 objects.
- A capped result is an incomplete result. `agent-dotfiles` signals this in the JSON and exits 3.

## Measurement before broader rollout

Benchmark representative repo tasks with the same fixtures, warm/cold cache conditions, match counts, output bytes, p50/p95 elapsed time and false/missed matches. Keep the existing agent-loop Map-vs-literal decision boundary. No tool wins solely by being new.

## Additional candidates (researched, not adopted as defaults)

| Candidate | Benefit | Caveat / recommendation |
| --- | --- | --- |
| `ast-grep` (never assume `sg`) | Structural non-PHP queries, JSON stream, source ranges | Optional experiment for TS/JS/etc.; Map is still primary for PHP when fresh. No `--rewrite`, `--update-all` or interactive mode. |
| Universal Ctags | Language-diverse symbol discovery with JSON lines | JSON requires build-time `libjansson`; verify `--list-output-formats` and selected parsers. Read-only, supplementary to Map. |
| `git log -S` / `-G` | Origin of changed literals/patterns | History is *not* proof of current callers; read chosen commit and source. No new dependency. |
| `git blame -L --line-porcelain` | Attribution of an exact range | Can be large; always scope lines, then inspect identified commits. |
| `git diff --binary --full-index` | Exact patch with binary reconstruction information | Larger output is intentional. Never replace with `--stat` during review. |
| `difftastic` | Human-oriented syntax diff | Presentation aid, not the canonical raw patch. Benchmark before adding. |
| `delta` | Human-oriented diff pager | Exclude from machine output by default (color/pager dependence). |

Sources: https://ast-grep.github.io/reference/cli/ ,
https://docs.ctags.io/en/stable/man/ctags-json-output.5.html ,
https://git-scm.com/docs/git-log , https://git-scm.com/docs/git-blame .

**Tool inventory is detection, not endorsement.** `doctor` reports optional
binaries; their mere presence does not change workflow routing or authorization.

## Explicit coding-agent profiles

`agent-dotfiles doctor` without `--profile` is the universal foundation: it
already checks Git and ripgrep and inventories optional tools. The existing
`minimal`, `git`, and `shell` profile names remain backward-compatible
diagnostic views, not separate environments users must opt into. The
non-executable `php` profile adds PHP readiness and optional Composer detection.
Select additional views through `agent-dotfiles doctor --profile`.
The JSON report states each declared required/optional tool, observed executable,
unavailable capability, and platform limit. It never installs a package, changes
PATH, sources user/project files, adds an alias, or picks a command for the
agent. `--strict` also fails when a selected profile lacks a required tool;
optional tools remain diagnostic-only.

For project commands, choose noninteractive, no-color and no-progress options
only after verifying the tool's actual supported flags. Keep error locations,
rule identifiers, complete selected diffs, and enough failure trace to diagnose
the next step. Output-byte reductions do not establish model-token or task-quality
improvements.
