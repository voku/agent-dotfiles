# Governed PHP maintenance and evidence-quality cycle — 2026-10-11

Owner: [dotfiles #12](https://github.com/voku/agent-dotfiles/issues/12).
Contracts: DOTFILES-17 (preflight repair, revision 2), DOTFILES-18
(evaluation/report, revision 1), LEARNING-164 (owner correction, revision 1).
No release, default activation or running-tool replacement occurred in this cycle.

## Revisions and boundaries

| Component | Immutable revision |
| --- | --- |
| Governing Loop, unchanged | `15507c3a313693eed45e2b1c98eda9c3aae7a7ef` |
| Real PHP source / separate scaffold runtime | `fad403a209d7d9f4438bf7036ce962780f44938c` |
| First-round optional toolset | `1e6e69bbf4bb0342acc4a42bca54cb00b418cb8d` |
| Second-round optional toolset / merged preflight | `79356188418c3cdb0d32f0d990e199f659e0666b` |
| Learning owner before / merged fix | `0995ce4fb26329088883c8b52259f5ed48875e05` / `d1df4e9085527af63427b9861054c83427e09d28` |

Optional tools were installed offline into separate private prefixes, verified,
and used explicitly. The second pin changes validation machinery; the runtime
CLI/profile implementation is unchanged. Loop has no dotfiles bootstrap dependency.
Each consumer used an ordinary separate clone and copied declared vendor dependencies.
The host, CPU and filesystem are shared: isolation was instruction-based, not an
OS sandbox. Incidental sibling command metadata seen through process diagnostics
is disclosed; no sibling source or private oracle was used by consumers.

## Finish the preflight before calling it evidence

Independent review of [PR #17](https://github.com/voku/agent-dotfiles/pull/17)
reproduced a passing read oracle with a wrong path and requested end despite
correct source bytes/hash. It also found missing installer-trigger paths and
cleanup skipped after a failed verification. The small fixes now check original
root/path/requested coordinates, trigger on installer/bin changes, and attempt
verification and safe uninstall independently while retaining both failures.
Installer refusal protections were not weakened. Three regression tests were added.

Reviewed head: `417425e55faa2216aa799df591a67fac48c8f324`.
[Exact-head tests](https://github.com/voku/agent-dotfiles/actions/runs/38140565956)
and [PHP preflight](https://github.com/voku/agent-dotfiles/actions/runs/38140565985)
passed. Merge: `79356188418c3cdb0d32f0d990e199f659e0666b`.
[Merged tests](https://github.com/voku/agent-dotfiles/actions/runs/38140710056)
and [explicitly pinned merged preflight](https://github.com/voku/agent-dotfiles/actions/runs/38140887008)
passed. The latter artifact records all 12 commands exiting zero, six parity checks,
post-use verification and uninstall. Local gates: 92 Python tests, compileall,
9 strict Bashunit tests. No new mutation run is claimed for this validation-only change.

Main advanced concurrently through unrelated Renovate work. A dispatch to `main`
therefore tested `488dd128497be551acd37624cab10b89eac14263`; that result is not
mislabelled as the PR17 merge. The separate validation branch pins the actual merge.

## Real PHP repairs, independently scored

An independent oracle injected two bounded defects into real production PHP code.
Original production is correct: these are seeded maintenance tasks, not discovered
production bugs. Existing inventory tests pass both broken seeds (19 tests /
39 assertions), so a new regression is necessary.

- First: a fresh old-version cache containing native tool entries hides installed
  external evidence tools. Preserve complete-cache reuse, refresh and project precedence.
  Seed: `33b46b83526f1fe5301cd36b97a212cb19d20b9a`.
- Held-out: an explicitly selected absolute cache path is written beneath the project.
  Preserve spaces/Unicode, relative paths and the default owner location.
  Seed: `86702524f6e48d30fdd8b5fd5aa884d261c8a1ba`.

All six Contracts approve only the actual owner class and its inventory test.
Public prompts describe behavior; private four-case black-box oracles and golden
patches were withheld until grading. B/C are **guided interface treatments**:
initial discovery/read must use standalone CLI or a guarded fresh profile, with
native verification/fallback permitted. This tests actual use, not natural routing.
The profile arms used Bash; Bash/Zsh parity is independently covered by PR17.

| Task | Native | CLI | Profile | Correctness / governance |
| --- | ---: | ---: | ---: | --- |
| Old-cache repair | 452.883 s | 427.705 s | 590.937 s | All 4/4; Learning closure blocked |
| Held-out absolute-cache repair | 262.965 s | 313.867 s | 320.706 s | All 4/4; all complete / next none |

Every strengthened regression independently fails the original seed. All source
changes preserve the exact approved two-file scope. Full Composer CI ultimately
passes each arm; the held-out suites execute 1,539 tests with one warning, one
PHPUnit deprecation and two skips. Focused tests execute 20 tests (48 assertions
native, 47 CLI/profile). Independent source hashes match the final commits:

| Held-out arm | Commit |
| --- | --- |
| Native | `3a4754fc06e359d334b4db349ab8a15b13669ccd` |
| CLI | `757017e89ebda4a25ae84fe82a2ca78ca99346a6` |
| Profile | `a2e89b2dd5f173a45309a9465de898d350033783` |

Final missing context: zero. False relevance: zero. Strict identical source-query
repeats: zero. Targeted follow-up reads and retries still occurred: B guessed
unsupported option placement, C's first-round default 80-line reads needed further
ranges. Completeness flags made that visible. These are not counted as identical
queries or silently omitted context. Raw traces preserve command errors, help calls,
validation retries and lifecycle work; some initial reads/procedural deviations
are disclosed in individual results rather than claiming perfect trace coverage.

Times cover consumer task work through closeout or blocker, including tests/retries.
Initial full-CI attempts hit the harness's 180-second timeout; a 600-second retry
was necessary. Cross-round tasks, timeout changes and shared CPU prevent causal
speed claims. Summed six consumer intervals: 2,369.064 seconds; this is not total
mission effort or elapsed parallel wall time. Actual per-agent model identity and
token telemetry are unavailable. Output bytes/hashes are evidence, never token estimates.

## The real Learning defect and fresh verification

The first-round fixture IDs were accepted by Loop but require a custom Learning
pattern. Capture honors that pattern; transition discarded it and failed root
validation. These correct PHP repairs remain **excluded** from completed governed
cycle proof. No owner artifacts were rewritten to fabricate closure.

Independent reproduction on current Learning also fails for `custom:27`.
[Learning #164](https://github.com/voku/agent-learning/issues/164) and
[merged PR #165](https://github.com/voku/agent-learning/pull/165) thread the optional
pattern through transition and response validation. The default regex stays strict;
mismatched patterns roll back exact candidate bytes. Full CI: 470 tests /
1,771 assertions, PHPStan zero errors; independent targeted review: 21 / 145.
[Exact-head CI](https://github.com/voku/agent-learning/actions/runs/38141312792)
and [merged-source CI](https://github.com/voku/agent-learning/actions/runs/38141429131)
passed PHP 8.3/8.4/8.5 and the installed-skill consumer. An intermediate regression-test
error is preserved and corrected, not hidden.

Two new owner consumers, including a space/Unicode directory and held-out `custom:73`,
execute 12 commands: capture, validation, unchanged no-op and strict rollback pass;
two intentional rejection commands exit 1. This verifies the owner correction in
fresh sessions. It is **unreleased** and not installed into the frozen Loop runtime.

Held-out trials use default-compatible `PHP-170x` IDs. They complete through
Session-linked validated Findings and canonical closeout. Loop's short `learn capture`
alias did not bind the supplied Session; consumers corrected this through the public
owner `finding-capture --session` command or typed `FindingCreator` API. Earlier manual
records and refused transitions remain disclosed. This does not claim the alias is fixed.

## Dream, validated lessons and limits

Dream was invoked after the preflight repair/integration, first-round grading,
Learning owner correction, and held-out completion. Owner consolidation inputs
include current validated findings plus previous
[evaluation](EVALUATION_2026-10-11.md) and [fresh dogfood](MOMENTUM_EXPERIMENTS.md).
The final dotfiles input selects six findings; the owner input selects one.

Each read-only Dream audit reports: evaluated guidance 0, warnings 0, review decisions 0,
suppressed decisions 0, selected guidance 0, explicit outcomes 0; outcome coverage is
null. This root contains validated findings but no active-guidance selection/outcome
history. Those zeros are a coverage limit, not proof of good guidance or an LLM
conclusion. Queues were inspected; no proposals were auto-approved, guidance promoted,
backlog archived or projections rebuilt. Host interpretation is separately labelled.

Validated lessons became structure: misleading evidence metadata is rejected by
regression tests; explicit owner validation configuration survives transition.
The held-out agents demonstrate repeatable correct repair and complete governance.
Comparative shell/CLI task quality or token advantage remains **INCONCLUSIVE**:
all arms are correct, errors/retrieval costs persist, token telemetry is absent,
and no improved runtime was tested. Keep #12 open; do not enable profiles by default.

## Reproduction evidence

[Immutable archive and independent report review](https://github.com/voku/agent-dotfiles/tree/67c55b0940ba3e136032560d669870a16c3442b3).
`quality-cycle-17.tar.gz` contains 1,199 payload files plus its manifest; SHA-256:
`ba65b00703026679099f801b660f9266c3a04c24d0a747cfd899485bd59717fb`.
Both builds are byte-identical. Seed/repair bundles, private-then-disclosed oracle,
original traces, failed attempts and owner states are preserved. Report source
snapshots precede this publication-link append; final closeout metadata follows
separately. Historical pending states are not current success claims.
