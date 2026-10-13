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
- The 0.7.0 friction log ([EVALUATION.md](../EVALUATION.md)) counts how often
  agents typed commands. It shows habits and failure modes, not that a wrapper
  improved a task outcome. Its weight differs per helper; see the table below.

## Decision

`agent-dotfiles` owns deterministic, non-interactive shell and environment
behavior. Nothing else.

1. **Native tools stay native.** A helper is allowed only if it is the native
   command with host-configuration bleed or interactivity removed and nothing
   else: the same arguments, output and exit status, with no change to what
   is searched, followed, hidden or counted. Two helpers meet this:
   `agent_git` and `agent_rg`. (`agent_diff` did not: see the table below.)
2. **One narrow exception: `agent_head`, an evidence-preservation primitive.**
   It does not replace or alter a native tool's behavior. It is the visible
   form of an operation the agent already performs (cutting a stream to N
   lines); what it adds is that the cut is announced with the true line count.
   Unlike `head` it also consumes all of stdin to count, so the producer is not
   cut off by SIGPIPE. It is justified by an observed failure mode, not by convenience:
   `| head` appeared in 6,148 of 12,121 observed shell calls, 2,097 of them
   after `rg`, each dropping the remainder without a word. That is evidence
   that the failure mode is common, **not** proof of better task outcomes
   (#69 showed none either way), so the exception stays small: no other
   output-bounding, paging or summarizing helper rides on it. It reads a
   text stream and prints its banner on stdout. Whether it
   changes outcomes is hypothesis H3 in #12.
3. **Environment defaults** (`agent.env`, `ripgreprc`) may remove progress
   bars, color, pagers, prompts and update nags. They must not change task
   semantics or hide evidence. `PYTHONIOENCODING` changed codec behavior and
   is removed.
4. **Task strategy is not a shell helper.** Choosing `rg` or `git grep`,
   proving a search complete, cross-checking results, deciding when to search
   binary files, linting a tree, orienting in a repository, archive policy:
   this is guidance for `voku/agent-skills` and workflow for agent-loop. This
   repository makes no completeness or correctness claim for it. A capability
   that stays useful may still belong to another owner.
5. **A new helper must name a failure mode and task evidence.** "Useful" or
   "called often" is not enough; neither is a passing corpus check. Reintroducing
   a removed helper needs that helper's own failure mode and a task where
   its absence changed a result, argued per helper.

## Helpers removed (recoverable from tag v0.7.0)

Judged individually. "Friction log" is the 12,121-call count in EVALUATION.md;
"none" means that log has no row for the habit.

| Helper | Friction-log evidence | Why it is not an exception | Owner of the capability |
| --- | --- | --- | --- |
| `agent_php_lint` | 478 `php -l` calls, 3 used `find`/`xargs` | Task strategy: which directories to skip, parallelism, a coverage claim. The corpus check proved only that it matched `find`; it needed bug fixes for interleaving and miscounts, i.e. maintenance cost for a task policy. | agent-skills (`php-static-analysis`) |
| `agent_context` | 427 `git diff --stat` calls | Repository orientation; reads `composer.json` and picks what to report. | agent-skills (`project-onboarding`) |
| `agent_extract` | 12 `tar`/`unzip` calls | Archive policy (traversal refusal, empty destination). The hazard is real, but it is a policy decision, not normalization, and the sample is tiny. | agent-skills guidance |
| `agent_require` | 227 `command -v`/`which` calls | Native `command -v` already answers it (ADR 0003); the version compare is extra policy. No observed failure mode. | none needed |
| `agent_curl` | none | `--location` follows redirects, hiding them, which contradicts the evidence rule. | none needed |
| `agent_history`, `agent_blame` | 86 `git log -p/-S/-G`/`blame` calls | `--literal-pathspecs` and `--line-porcelain` change pathspec semantics and output format; no observed failure of native Git. | none needed |
| `agent_diff` | 427 `git diff --stat` calls (not specific to it) | `--no-ext-diff --no-textconv` is not host noise: external diff drivers and textconv filters may be repository-defined, so the output can differ from native `git diff` evidence. Choosing a raw, apply-able patch is task strategy; explicit guidance, not a second exception without independent task evidence (owner review of #72). | agent-skills guidance |
| `agent_diff_check` | none | Two native commands in sequence. | none needed |
| `agent_root`, `agent_mkcd` | none | Change the shell's directory; navigation, not normalization. | none needed |
| `agent_usage` | 43 `du` calls | `du -h -d 1`; no failure mode. | none needed |
| `agent_codepoints` | none | Niche diagnostic with no observed use. | skill, if a task needs it |

## Contract kept narrow

`agent_rg` is `rg --no-config --color=never`. It does **not** guarantee that
every matching file is listed: a file ripgrep classifies as binary (a NUL
byte) is skipped during recursive traversal, silently, exit 0. The regression
test `test_agent_rg_is_native_ripgrep_and_inherits_its_binary_file_limitation`
keeps that limitation as evidence. A caller who needs a complete inventory
chooses and verifies the method; that is task strategy.

## Consequences

A smaller surface to be wrong, with one deliberate evidence-preservation
exception. Open questions are tracked per helper in #12, not as features here.
