# Steady-state coding-agent evaluation

Status: **protocol proposed, not executed** (2026-10-12). This supersedes the *measurement methodology*, not the archived raw measurements, in [the October 11 evaluation](EVALUATION_2026-10-11.md). Execution and independent grading belong to [issue #12](https://github.com/voku/agent-dotfiles/issues/12).

## Product hypothesis

An agent-specific, pre-installed development environment with trustworthy commands and scoped defaults increases **correctly completed maintenance tasks** over a sequence of tasks. Workflow, Recall and reviewed project knowledge remain owned by the independently installed `agent-loop`, identical across treatments. A smaller command output or shorter bootstrap does not prove the environment hypothesis. The unit of benefit is the correctly completed task.

**Setup is paid once per installation**; it is not part of each task's latency. Also distinguish setup on a new host, one-time onboarding for a new project, and repeated operations such as shell activation. A recurring operation must not be mislabeled a one-time cost, and a one-time installation must not be charged once per fresh agent session.

## Two separate accounting ledgers

1. **One-time investment:** record host installation, download/verification, initial configuration and project onboarding as `S_host` and `S_project` with provenance. These occur outside the task timer and **once per matching environment/project**. Include future updates only when an actual update happens.
2. **Warm task ledger:** with the **same pinned, installed environment** reused, start timers after each task is assigned. Include every real per-task action: optional activation, tool calls, model inference, retries, tests, waits for human intervention (record separately), debugging and completion. **Do not reinstall** a tool or repeat onboarding to simulate a fresh coding agent. If a task really needs reconfiguration, measure and disclose that recurring cost.

For `N` completed tasks in an already installed environment, report the empirical mean/median of `T_baseline` and `T_env` independently of the setup ledger. For lifetime economics, report:

```text
Baseline total(N) = S_baseline + sum(task_time_baseline[i], i=1..N)
Agent total(N)    = S_host + S_project + sum(task_time_agent[i], i=1..N)
Net time saved(N) = Baseline total(N) - Agent total(N)
```

`S_baseline` includes any fair baseline provisioning shared with the agent condition. Do not double charge a shared bootstrap (for example the common CI runner or agent-loop install). If paired tasks show a stable per-task improvement `delta > 0` and *incremental* one-time setup `S > 0`, the illustrative break-even is `ceil(S/delta)` tasks; if `delta <= 0`, there is **no demonstrated time-only payback**. Prefer actual cumulative measurements with confidence/uncertainty over projecting one noisy run.

## Control the factors instead of comparing unrelated products

Run the same *independently graded*, frozen task set on pinned copies of the same repository and dependencies. Match provider/model/settings, instruction budget, agent-loop policy, host resources, human intervention rules and timeouts. Counterbalance task order to reduce learning/order effects; prevent shared working trees and cross-arm caches that leak solutions.

Use **three environment treatments**, all with the same pinned `agent-loop`
workflow, reviewed knowledge (if any), source revision and native tools:

| Arm | Optional dotfiles environment |
| --- | --- |
| A: native baseline | No `agent-dotfiles`; direct native `git`, `rg` and approved project tools |
| B: installed CLI | Same baseline plus one verified, pinned private-prefix `agent-dotfiles` CLI; no shell activation |
| C: installed CLI and shell | Same pinned CLI plus explicitly sourced Bash **or** Zsh profile |

Do not change the agent-loop version, workflow policy, Recall input, memory
snapshot or agent task prompts by arm. If durable reviewed knowledge exists,
provide the **same** frozen knowledge to all arms. Studying whether Learning
helps future tasks is an independent `agent-loop` experiment, not an
`agent-dotfiles` benefit claim.

Agents may choose native commands in every condition; do **not** force an
optional tool invocation or handicap the baseline. Keep agent-model sessions
fresh between tasks while reusing the **already installed host tooling**.
Counterbalance task order and separate working trees/caches so no solution
leaks between arms. Compare Bash and Zsh as an explicit compatibility check,
not a hidden fourth product treatment.

## Score actual agent results

Primary quality gate: independently grade correct completion **and** source completeness, approved task scope, test/static-analysis safety, no fabricated evidence, and no silent error masking. A faster incorrect answer is a loss, not a performance win.

Secondary observations: task wall time, observed input/output/cached model tokens (only when provider telemetry exists), developer interventions, number and reason for failed attempts, redundant retrieval, relevant evidence missed, security regressions, and number of correctly completed tasks per hour or model-cost budget. Track task failures separately; do not average them out by timing only successful solutions.

Every run records its exact model identity if available, candidate SHA, installed manifest, project SHA, common agent-loop revision and reviewed-knowledge SHA (if applicable), task ID, treatment, reused installation ID, timing boundaries, command receipts including nonzero exits, independent oracle result and missing telemetry as `unknown`. Record raw provenance outside the product checkout; optionally publish redacted evidence with a reproducibility guide.

## Use existing GitHub Actions without pretending they execute an LLM

Keep [the cold-install CI](../.github/workflows/test.yml) for the **once-per-version correctness gate**. Reuse its verified pinned consumer prefix across multiple tasks **inside a future agent-host evaluation**, not a separate reinstall for each task. The existing [real PHP preflight](../.github/workflows/real-php-preflight.yml) proves **command parity only**. A CLI subprocess timing loop, GitHub Actions matrix or generated token byte count is not a real agent-outcome experiment. A real coding-agent run requires an explicit approved host/runtime and provider credentials or an independently supported non-network local agent, plus independent grading.

Practical held-out workloads:
- A known-repository PHP/PHPStan fix where the correct file is already supplied (negative control: wrappers should add little).
- An unfamiliar PHP/Shell regression requiring discovery, exact diff and clean test execution (search/evidence benefit).
- A follow-up maintenance issue where a new agent session reuses the same pinned host environment without repeated installation (environment-retention benefit).
- A misleading path with newlines, binary patch, or truncated output (safety and honest evidence; verify error detection).
- An intentionally absent optional capability (degradation should be explicit and native fallback should work).

## Bounded acceptance evidence: 2026-10-12

Four useful cycles were completed from remote main
`103bd188ae92b805823a204bb07ffbd7df679caa`, after confirming no open PRs and
inspecting merged #51/#52 plus Redpill source
`79333d8dda8131732e44574e0dc089a8b47f70cf`. Changes add lifecycle proof,
complete onboarding commands, portable test execution and a controlled search
comparison. The full multi-agent warm-task protocol above remains **unexecuted**.

| Criterion | Observable evidence and scope |
| --- | --- |
| Onboarding | [Complete recipe](INSTALLATION.md#complete-fresh-project-walkthrough): explicit parent creation, pinned plan/install/verify, strict doctor, fresh Bash/Zsh activation, deactivate and uninstall. |
| Reproducibility | [Two-consumer regression](../tests/test_installation.py): byte-identical manifests and source-read output at one pin, both consumers verified and removed. Equivalent behavior is for the same inputs/host, not identical absolute paths on different machines. |
| Safety | The same regression snapshots HOME, project and source before/after; existing tests reject occupied prefixes and modified removals. [Ownership tests](../tests/test_repository_ownership.py) and tracked-state installation fixtures exclude Loop state and project memory. |
| Compatibility | Require the **exact final PR commit**, not its base or synthetic merge, to pass [the entire matrix](../.github/workflows/test.yml). The final run URL/SHA and artifacts are recorded in the PR. Local validation alone cannot satisfy this gate. |
| Usability | The current real Codex session explicitly installed and used the candidate below to verify a real Python-only-host regression: doctor, workspace, search, hashed read and the targeted test. This is one operator session, not an independently graded agent comparison. |
| Value | The fixed search correctness oracle below measured 1/4 native vs 4/4 preset. Explicit native `--no-config` also scored 4/4; broader productivity and efficiency remain **INCONCLUSIVE**. |

Consumer task pin: `1f7e809d173c1f36c22e31bf11d28a29a3a2ea45` (52 payload files).
Codex session: `01a13056-e86b-76d2-bb41-41d9515b1b7f`; Loop source:
`d1a6939a8ecb671dbe17f46e86a6fcdae63ef309`. Installed commands found
`symlink_to(sys.executable)` at `tests/test_mutation_workflow.py:28`, retrieved
lines 21–33 with whole-file digest
`1135f22e41a7bcda9e1ad303c2be61fc6f52e70e3c40cddd40af4b7d1442729d`,
and the representative verification test passed. Verify also passed after use;
uninstall removed only the 52-file temporary consumer. No new LLM process or
provider credentials were required. Final-commit CI independently repeats cold
installation; the operator task pin is recorded separately and is not final CI.

Predefined metric: exact case-sensitive literal match lines, stdout, stderr and
exit status for `TOKEN` in a three-line `TOKEN / token / TOKEN` fixture.
Four configurations: empty, `--ignore-case`, `--glob=!*.py`, `--max-count=1`.
All arms use the same fixture, PATH, shell and arguments; only the invocation
changes. Native configuration contamination causes an extra match, no matches,
or a missing match respectively. The oracle is fixed expected text, not output
copied from the treatment. No output-byte or timing proxy is graded.

| Arm | Correct cases on local Bash | Interpretation |
| --- | ---: | --- |
| Plain native `rg` | 1/4 | Inherits deliberately supplied host configuration. |
| Reviewed `agent_rg` preset | 4/4 | Isolates configuration per invocation. |
| Native `rg --no-config` | 4/4 | Same correctness when isolation is explicit. |

Reproduce with `python3 -m unittest discover -s tests -p test_shell_profiles.py -v`.
The test emits all 12 raw command-result receipts per available shell as JSON;
CI contract-test artifacts preserve them. Local versions: Python 3.11.2,
Bash 5.2.15, ripgrep 15.2.0; Zsh is absent locally and required in CI.
This demonstrates a narrow reliability property of an existing preset, not a
unique algorithm or real-agent throughput advantage. Both guided implementation
and Learning closeout used Loop; read-only Dream after meaningful steps reported
0 evaluated guidance, 0 warnings, 0 decisions, 0 suppressed decisions and no
outcome coverage. An empty Learning root is not evidence of effective Learning.

## Decision gate

Publish per-task results and aggregate results, including all failed trials. Adopt by default only if the whole environment increases correctly completed tasks or otherwise demonstrates an independently verified improvement for the stated use case, without unacceptable safety/context loss. No compulsory global aliases or automatic package downloads on the strength of setup timing, CLI output size or a green CI alone. A null result is useful evidence against unnecessary wrappers; it does not imply specialized tooling has no value in other tasks. Claims about cross-task memory effectiveness belong to the agent-loop owner and require a separate controlled comparison.
