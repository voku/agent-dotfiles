# Steady-state coding-agent evaluation

Status: **protocol proposed, not executed** (2026-10-12). This supersedes the *measurement methodology*, not the archived raw measurements, in [the October 11 evaluation](EVALUATION_2026-10-11.md). Execution and independent grading belong to [issue #12](https://github.com/voku/agent-dotfiles/issues/12).

## Product hypothesis

An agent-specific, pre-installed development environment with trustworthy commands, scoped defaults and *reviewed project learning* increases **correctly completed maintenance tasks** over a sequence of tasks. A smaller command output or shorter bootstrap does not prove that hypothesis. The unit of benefit is the completed task and, over time, the repository's retained knowledge.

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

Use **four conditions** where feasible:

| Arm | Pinned agent tools | Project-local reviewed knowledge |
| --- | --- | --- |
| A: native baseline | No | No |
| B: tooling only | Yes; private-prefix CLI and explicit Bash/Zsh functions available | No |
| C: knowledge only | No | Yes; identical reviewed `MEMORY.md`/ADRs/finding set |
| D: whole product | Yes | Yes |

All arms retain the same baseline agent-loop governance, compiler, and native Git/rg access. Give agents the same *accurate* usage guidance where applicable; do **not** force optional tool use, or make the baseline solve an intentionally handicapped task. Keep agent-model sessions fresh to test whether environmental state survives handoff, while reusing the **already installed host tooling**.

A/B reveals tool impact; A/C reveals knowledge impact; B/D reveals incremental knowledge value when tools are present; A/D evaluates the whole product. When only a three-arm experiment is affordable, report **which causal comparison is missing** rather than implying one factor explains an outcome.

For cross-task memory, separate *training tasks* from an independently authored **held-out future task**. Permit only reviewed, appropriately redacted, versioned findings from training to enter the next task. Do not store the evaluator's secret tests, solution patch, prompts with expected answers, private data, or transient session histories in project memory. Freeze that reviewed state and record its SHA in each eligible arm. The baseline may be evaluated both with and without identical knowledge for fairness and attribution.

## Score actual agent results

Primary quality gate: independently grade correct completion **and** source completeness, approved task scope, test/static-analysis safety, no fabricated evidence, and no silent error masking. A faster incorrect answer is a loss, not a performance win.

Secondary observations: task wall time, observed input/output/cached model tokens (only when provider telemetry exists), developer interventions, number and reason for failed attempts, redundant retrieval, relevant evidence missed, security regressions, and number of correctly completed tasks per hour or model-cost budget. Track task failures separately; do not average them out by timing only successful solutions.

Every run records its exact model identity if available, candidate SHA, installed manifest, project SHA, memory SHA, task ID, treatment, reused installation ID, timing boundaries, command receipts including nonzero exits, independent oracle result and missing telemetry as `unknown`. Record raw provenance outside the product checkout; optionally publish redacted evidence with a reproducibility guide.

## Use existing GitHub Actions without pretending they execute an LLM

Keep [the cold-install CI](../.github/workflows/test.yml) for the **once-per-version correctness gate**. Reuse its verified pinned consumer prefix across multiple tasks **inside a future agent-host evaluation**, not a separate reinstall for each task. The existing [real PHP preflight](../.github/workflows/real-php-preflight.yml) proves **command parity only**. A CLI subprocess timing loop, GitHub Actions matrix or generated token byte count is not a real agent-outcome experiment. A real coding-agent run requires an explicit approved host/runtime and provider credentials or an independently supported non-network local agent, plus independent grading.

Practical held-out workloads:
- A known-repository PHP/PHPStan fix where the correct file is already supplied (negative control: wrappers should add little).
- An unfamiliar PHP/Shell regression requiring discovery, exact diff and clean test execution (search/evidence benefit).
- A follow-up maintenance issue where a *reviewed* earlier decision prevents repeating a documented failure (memory-retention benefit).
- A misleading path with newlines, binary patch, or truncated output (safety and honest evidence; verify error detection).
- An intentionally absent optional capability (degradation should be explicit and native fallback should work).

## Decision gate

Publish per-task results and aggregate results, including all failed trials. Adopt by default only if the whole environment increases correctly completed tasks or otherwise demonstrates an independently verified improvement for the stated use case, without unacceptable safety/context loss. No compulsory global aliases or automatic package downloads on the strength of setup timing, CLI output size or a green CI alone. A null result is useful evidence against unnecessary wrappers; it does not imply that retained decisions or specialized tooling have no value in other tasks.
