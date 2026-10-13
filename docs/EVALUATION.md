# Evaluation

Owner: [#12](https://github.com/voku/agent-dotfiles/issues/12). Rule from
[AGENTS.md](../AGENTS.md): no default activation is recommended until the
controlled agent trial in layer C has been run. Correctness and complete
evidence outrank output-byte reductions; nothing here claims token savings or
productivity.

| Layer | Question | Status (0.7.0) |
| --- | --- | --- |
| A. Corpus check | Does each remaining helper give the same evidence as clean native commands on real code, in Bash and Zsh? | Run, repeatable: `tests/eval/corpus_check.sh` |
| B. Friction log | Which shell habits do agents really have, and so which helpers earn a place? | Done once, 12,121 calls (below) |
| C. Agent trial | Do agents with the environment finish real tasks at least as correctly, with at least as complete evidence? | **Protocol only, not run** |

## A. Corpus check

`tests/eval/corpus_check.sh [-n MAX] [-s bash,zsh] DIR_OR_REPO...` activates the
profile in a fresh shell and, per repository, checks:

| Check | Passes when |
| --- | --- |
| `rg-insulated`, `rg-exit-status` | `agent_rg` under a hostile `RIPGREP_CONFIG_PATH` (column limit, glob, max-count, color) returns the same lines and exit status as clean `rg --no-config` |
| `rg-plain-no-hidden-matches` | plain `rg` with the activated config returns the same lines as clean native `rg` |
| `diff-insulated` | `agent_diff HEAD~1 HEAD` under a hostile global gitconfig (forced color, broken external driver, pager) is byte-identical to a clean native diff |
| `head-announces` | `agent_head 25` shows 25 lines and announces the true total |

Output order of `rg` differs between identical runs (parallel walk), so `rg`
results are compared as sorted line sets. The script reads repositories and
writes only to a temporary directory. It does not measure speed, model tokens
or productivity.

### Result, 2026-10-13

Linux container (Debian bookworm, PHP 8.2), both shells, nine real PHP
repositories from 6 to about 12,700 files: **126 passed, 0 failed** (9 repositories × 2 shells; the largest, IT-Portal and phpstan-src, took 169–300 s per shell, almost all of it linting).

What it found and fixed before release:

- `agent_php_lint` took 149 s for 1,682 files; it now runs in parallel (37 s).
- Parallel reports first interleaved and miscounted (most files "unchecked");
  each report is now written in one piece and a file php never reports on
  fails the run. Both are covered by regression tests.
- `rg` ordering is nondeterministic; documented, not changed.

After [ADR 0004](decisions/0004-environment-vs-task-strategy.md) the corpus
check covers `agent_rg`, `agent_diff`, activated plain `rg` and `agent_head`
(`head-announces`: `agent_head 25` shows 25 lines and announces the true
total). Checks for the removed helpers (`php-lint-coverage`,
`context-package`) were deleted with them. The 2026-10-13 result above was recorded at 0.7.0 with
those checks.

## B. Friction log

Counts from 70 local Claude Code transcripts (12,121 Bash calls, one
developer, PHP-heavy work). Commands were counted, never stored or quoted.

| Habit | Calls | Consequence |
| --- | ---: | --- |
| `… \| head` (any) | 6,148 | Silent truncation is the dominant habit; the basis for the `agent_head` exception (ADR 0004). Habit frequency, not an outcome result |
| `rg … \| head` | 2,097 | Search results cut with no notice; `agent_rg … \| agent_head 50` announces the cut |
| `rg` | 5,111 | Plain `rg` presentation defaults (`ripgreprc`); `agent_rg` for host-config insulation |
| `git diff --stat` | 427 | Native; `agent_diff` only normalizes. Orientation is skill territory (`agent_context` removed) |
| `php -l` | 478 | Native; only 3 used `find`/`xargs`. Linting strategy belongs in a skill (`agent_php_lint` removed) |
| `command -v` / `which` | 227 | Native `command -v` is enough (`agent_require` removed) |
| `git log -p/-S/-G`, `blame` | 86 | Native Git (`agent_history`, `agent_blame` removed) |
| `du` | 43 | Native `du` (`agent_usage` removed) |
| `tar` / `unzip` | 12 | Archive policy is skill territory (`agent_extract` removed) |
| `ss`/`lsof`/`netstat` | 8 | Dropped `agent_ports`, `agent_free_port` |
| `json.tool` | 4 | Dropped `agent_json` |
| `uname`/`lsb_release` | 3 | Dropped `agent_os` |

A helper only helps if the agent calls it. The habit data says the guidance
("never a bare `| head`") matters more than another wrapper; that guidance is
in [SHELL.md](SHELL.md) and belongs in the `agent-skills` onboarding skill.
Limits: one developer, one stack, and counts show use and failure modes, not
whether the output was complete or a task went better. Do not call a helper
this table marks as removed; it no longer exists (recover from `v0.7.0`).

### Pilot #69 (one triplet, closed)

Final answers were identical and correct in all arms; the guided arm used more
calls and time; treatment isolation and activation were not proven, so there
is no valid comparative effect. It exposed the `agent_rg` NUL limitation (#70).
Raw transcripts are local and not part of this repository.

Open hypotheses, each small and testable under a new protocol with isolation
and an activation proof, none a feature request:

- H1: with the profile active and no guidance, agents truncate or miss
  evidence no more often than native (regression check only).
- H2: guidance about cross-checking inventories (agent-skills) reduces
  incomplete answers more than any shell helper does.
- H3: `agent_head` (the one evidence-preservation exception): when the
  profile is active, agents whose output was cut by it state the cut in their
  answer more often than agents using a bare `| head`, and no answer is less
  correct. Outcome benefit is unproven; if the data show no difference, remove
  it.
- H4: removing `PYTHONIOENCODING` matters for no scored task.

No hypothesis covers "the removed helpers" as a group. Reintroducing one needs
its own helper name, failure mode and task evidence (ADR 0004, rule 5).

## C. Agent trial protocol (not yet run)

**Arms** (same model, host, prompt, repository commit and time limit):
1. native: host defaults, no profile;
2. env: profile activated, no extra guidance;
3. env + guidance: profile activated, helpers named in the task prompt.

**Tasks** (real repositories at a pinned commit, each with a held-out oracle
produced independently of the agent, ≥3 repetitions per arm):

| Task | Trap / oracle |
| --- | --- |
| T1 list every caller of a symbol in a large repo | exact set from `git grep`; >500 matches tempts truncation |
| T2 report every PHP syntax error in a repository | sequential `php -l` set |
| T3 describe an uncommitted change set | planted changes incl. rename and whitespace-only |
| T4 explain where a setting is read | pre-written answer with file:line |
| T5 install dependencies and run the test suite, report failures verbatim | prompts, progress bars, exit status |
| T6 who introduced a string, and when | `git log -S` answer |
| T7 unpack a supplied archive and list contents | archive holds a `../` entry |
| T8 count matches of a pattern in a 10k-file repository | exact count |

**Record per run:** final answer, correct/incorrect against the oracle,
evidence complete (did the transcript show every item reported?), hangs,
prompts, truncations noticed, wall time, tool calls, model tokens where the host
exposes them (otherwise "unavailable", never estimated from bytes).

**Decision rule.** Recommend the profile as the *documented default for a host*
only if, across ≥2 hosts, no task is less correct than native, no arm-2/3 run
hangs or truncates silently, and every difference in time or calls is reported
without being turned into a productivity claim. Otherwise keep it opt-in. If
the arms are indistinguishable, say so and stop growing the profile.

Running layer C needs real agent sessions and their own agent-loop Contract.
It is deliberately not simulated here.
