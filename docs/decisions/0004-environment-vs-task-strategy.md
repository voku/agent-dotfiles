# ADR 0004: Environment normalization only; task strategy lives in guidance

- Status: Accepted (proposed in the review of #12, #69 and #70)
- Date: 2026-10-13
- Context: the #69 pilot, #70 and [docs/EVALUATION.md](../EVALUATION.md)

## Evidence

- #69 (n=1 per arm): native, profile and guided arms gave the same correct
  final answer. The guided arm cost more calls and time. Profile activation
  was not evidenced and the native arm could see this checkout, so there is
  **no valid comparative effect**.
- #70: `agent_rg` is native ripgrep and inherits its silent skipping of
  NUL-containing files in recursive search. Making it a completeness tool
  (default `--binary` or `-a`) would widen the helper to search images,
  archives and databases for every navigation query. The first #70 decision
  comment chose a default `--binary`; it was revised. `agent_rg` stays native.
- The 0.7.0 friction log counts how often agents typed commands. It shows
  habits, not that a wrapper improved a task outcome.

## Decision

`agent-dotfiles` owns deterministic, non-interactive shell and environment
behavior. Nothing else.

1. **Native tools stay native.** A helper is allowed only if it is the native
   command with host-configuration bleed or interactivity removed and nothing
   else: the same arguments, output and exit status, with no change to what
   is searched, followed, hidden or counted. Three helpers meet this:
   `agent_git`, `agent_rg`, `agent_diff`.
2. **Environment defaults** (`agent.env`, `ripgreprc`) may remove progress
   bars, color, pagers, prompts and update nags. They must not change task
   semantics or hide evidence. `PYTHONIOENCODING` changed codec behavior and
   is removed.
3. **Task strategy is not a shell helper.** Choosing `rg` or `git grep`,
   proving a search complete, cross-checking results, bounding output,
   deciding when to search binary files, linting a tree, orienting in a
   repository, unpacking archives: this is guidance for `voku/agent-skills`
   and workflow for agent-loop. This repository makes no completeness or
   correctness claim for it.
4. **A generic helper must justify itself with outcome evidence**, such as a
   controlled run (#12) where it changed a correctness or evidence result,
   not with plausibility, call frequency or a passing corpus check.

## Helpers removed (recoverable from tag v0.7.0)

| Helper | Why it is not environment normalization |
| --- | --- |
| `agent_head` | Output-bounding policy; its banner is mixed into the data stream. Guidance ("never cut evidence with a bare `\| head`") belongs in a skill. Frequency of `\| head` in the friction log is a habit count, not an outcome result. |
| `agent_php_lint` | Task strategy: which directories to skip, parallelism and a coverage accounting claim. Owned by a PHP skill. |
| `agent_context` | Repository orientation is the onboarding skill's job. |
| `agent_extract` | Archive-safety policy, 12 uses in 12,121 calls. |
| `agent_require` | ADR 0003 already says `command -v` covers capability checks. |
| `agent_curl` | `--location` follows redirects, which hides them. |
| `agent_history`, `agent_blame`, `agent_diff_check`, `agent_root`, `agent_mkcd`, `agent_usage`, `agent_codepoints` | Thin or convenience wrappers with no outcome evidence; `agent_root` and `agent_mkcd` change the shell's directory. |

## Contract kept narrow

`agent_rg` is `rg --no-config --color=never`. It does **not** guarantee that
every matching file is listed: a file ripgrep classifies as binary (a NUL
byte) is skipped during recursive traversal, silently, exit 0. The regression
test `test_agent_rg_is_native_ripgrep_and_inherits_its_binary_file_limitation`
keeps that limitation as evidence. A caller who needs a complete inventory
chooses and verifies the method; that is task strategy.

## Consequences

Fewer things to maintain and a smaller surface to be wrong. Hypotheses that
would justify adding anything back are tracked as small questions in #12, not
as features here.
