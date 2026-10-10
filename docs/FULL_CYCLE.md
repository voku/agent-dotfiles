# Governed full-cycle report — 2026-10-10

**Persistent empty-file range correctness improvement: PROVEN in the tested cases.
Overall full-cycle productivity improvement: INCONCLUSIVE.** Native tools remain
the default. An optional reviewed release does not establish token or efficiency
savings and does not change agent-loop policy.

## Scope, revisions and authority

User approved the full agenda, including reviewable changes, normal PR integration
and approved releases. Builder tasks used actual agent-loop `enter`, approved
Contracts, L1 preparation, validation, review and Learning closeout. LOOP-757
integrated existing work; DOTFILES-9 owns production installation and evaluation.
No human review or permissions were fabricated. Independent agents reviewed
repairs, installation, production code and benchmark results.

| Repository / role | Exact commit |
| --- | --- |
| agent-dotfiles original main | 8d228138f3b12a12b2b0c1338534f98e5fe35578 |
| agent-dotfiles integrated main / candidate v1 | b6e339cdec2dcafcbfc52ca9020b3fbba9964ff2 |
| agent-dotfiles installed candidate v2 runtime | 8fa00fd30ab30025aacd99108ae51ba7e27bba86 |
| agent-loop builder source | 622c004e2cc642fce1c06dc63a4f04d4889637e2 |
| agent-loop all fresh consumers, release 0.20.64 | 15507c3a313693eed45e2b1c98eda9c3aae7a7ef |
| agent-map inspected source | 9feade3b6edf43c772bda7eb3fe00e6ca323a757 |
| agent-learning inspected source | d9b83da0a5a0388637a126c14bc9b509802b3b49 |
| agent-recall-compiler inspected source | afc94971c35700c8b9f449368da347281752252f |
| original interactive dotfiles, read-only research | 79333d8dda8131732e44574e0dc089a8b47f70cf |
| identical consumer task baseline | 33003d8dc5f52c77c02d353804db0c04345f6f27 |

All thirteen workspace source revisions are in
[the source manifest](benchmarks/2026-10-10/all-source-revisions.json).
The final release source commit is recorded in its release metadata and Git tag;
the candidate runtime above stayed immutable during evaluation. Consumer Loop
dependencies were reused from the working builder installation, with regenerated
autoload, platform checks and 1,391 fast tests passing (one warning, one
deprecation). No library lockfile was present. The
[91 dependency source references](benchmarks/2026-10-10/loop-runtime-dependencies.json)
freeze the actual toolset; this is not a claim that a new unconstrained Composer
resolution will reproduce it. All four consumers used the same unchanged toolset.

## Existing work and validation

- [PR #4](https://github.com/voku/agent-dotfiles/pull/4) merged as
  `b9d5d687cadb21c5b8649f675c3446b51007b94d`. A real regression test caught
  mutation-report failure suppressing GitHub's summary; the fix preserves both
  diagnostics and nonzero status.
- [PR #6](https://github.com/voku/agent-dotfiles/pull/6) merged as
  `3a2be986f67ffd7a804d0effd42aca10e1136a8d`. Independent review added RED/GREEN
  regressions for subdirectory patch scope and bounded index output. Literal
  file identity, complete native patch bytes and hashes were verified independently.
- [PR #8](https://github.com/voku/agent-dotfiles/pull/8) merged as
  `b6e339cdec2dcafcbfc52ca9020b3fbba9964ff2`, after synchronization and fresh checks.
  Individual untracked files are exposed with `--untracked-files=all`.
- [Issue #9](https://github.com/voku/agent-dotfiles/issues/9) and
  [PR #10](https://github.com/voku/agent-dotfiles/pull/10) carry the production slice.
  Parent tasks are Loop [#757](https://github.com/voku/agent-loop/issues/757),
  [#756](https://github.com/voku/agent-loop/issues/756), and original research
  [dotfiles #48](https://github.com/voku/dotfiles/issues/48).

Fresh CI passed on each integrated PR head and main. Production code at
`8fa00fd` passed 72 Python tests, Bashunit 0.50.1 (8 tests, 19 assertions),
compilation and independent review. Fresh CI at `3c0ecee5248e4628742a7d362d951f230f9b74f8`
passed Python 3.10/3.12/3.13, Bashunit and the complete macOS Python suite.
The first macOS run exposed test fixtures using the `/var` symlink; canonical
private fixture paths repaired setup without weakening symlink refusal.
CI retains logs, machine-readable capability diagnostics and mutation artifacts.
Final integration checks are bound to the final source commit in release metadata.

Focused Cosmic Ray 8.7.0 path/limit testing: **51 mutants, 49 killed, 2 survived**;
no pending, timeout or worker-error result was treated as success. The surviving
equality-to-identity string comparisons are probable equivalents for exercised
CLI/path semantics, not proven universal equivalence. Coverage is deliberately
focused on validation guards; it does not establish exhaustive mutation coverage
of installation or every runtime operation. Genuine installer and range defects
were independently reproduced with precise failing tests before correction.

## Installation and optional consumption

The [installer contract](INSTALLATION.md) is offline, explicit and full-SHA pinned.
Real isolated installations of v1 and v2 were verified; B2 used the installed v2
executable by absolute path. After consumers ended, v2 still verified, removal
succeeded, v1 rollback invocation succeeded and v1 removal succeeded. Modified,
unexpected, symlink and invalid-manifest states refuse removal and preserve files.
Doctor reports missing capabilities without failing unless strict mode is selected.

Builder, validators and consumers used separate source directories and installation
prefixes. They share one cloud host, so this is filesystem/session separation,
not proof of separate-machine isolation. No running toolset was replaced.
A1/A2 start, govern and finish without optional agent-dotfiles context routing.
No global installation, PATH/Git/shell change, remote installer or interactive
dotfiles sourcing occurred. History/blame and structural PHP remain native Git
and agent-map responsibilities. [Consumer routing](AGENT_LOOP.md) is manual and
opt-in; no always-on host projection or owner policy change is justified by these
results.

## Controlled tasks and measured outcomes

Fresh agents with the same inherited model settings used identical starting Git
states. A used native evidence tools; B used pinned optional tools. Tasks covered
an ambiguous PHP symbol and callers, config/template references, history across
two files, literal bracket pathspec patch evidence, unusual Unicode/newline paths,
untracked and ignored files, and a real failing Python regression. The oracle was
frozen independently before reading results; second-run fixtures were separately
held out. The PHP/config fixtures are small and synthetic, not a production PHP
application or proof of actual invoice rendering.

| Metric | A1 | B1 | A2 | B2 |
| --- | ---: | ---: | ---: | ---: |
| Final required evidence correct | yes | yes | yes | yes |
| Missing required fixture context | 0 | 0 | 0 | 0 |
| Incorrect relevance in final selected evidence | 0 | 0 | 0 | 0 |
| Python / Bashunit independently passed | 58 / 6 | 58 / 6 | 58 / 6 | 58 / 6 |
| Raw trace records | 50 | 64 | 31 | 64 |
| Leaf records, excluding nested wrapper parents | 50 | 57 | 31 | 61 |
| Strict redundant same-scope retrievals | 0 | 1 | 0 | 2 |
| Approximate total session wall time, seconds | 297.5 | 309.3 | 149.0 | 190.2 |
| Leaf subprocess elapsed sum, seconds | 13.73 | 14.97 | 16.56 | 21.98 |
| Measured model tokens | unavailable | unavailable | unavailable | unavailable |

First-run initial wall times were 167.4/161.9 seconds. Shared missing PHP `PHPRC`
and uninitialized Learning storage blocked fresh Map/closeout; equal supported
repairs and successful reruns are preserved alongside initial receipts. Total
first-run time includes waiting. Second runs started after those repairs.
A1/B1 omitted Bashunit in their traces; the independent evaluator ran it. A2
disclosed one unwrapped initial prompt read. These process deviations are retained.

Leaf counts remove overlapping wrapper records, but native Python scripts batch
some subprocesses while B often traces them individually. Counts are not identical
units of all underlying calls. Starts were recorded just before spawns and wall
time is approximate. Concurrent agents on one host, different reasoning choices,
two pairs and prerequisite repairs prevent a causal speed conclusion. No p50/p95
or token saving is inferred from these data or output bytes. Standalone Codex
execution failed authentication; fresh collaboration agents supplied the actual
comparison, without token telemetry.

A1 initially fetched an unrelated bracket-matching patch and corrected it before
submission. B1/B2 correctly handled Git-root-relative inventory paths despite a
subdirectory selection. Broad inventories and earlier history returned extra
context during investigation. Final selected evidence contained no unrelated
patch or substituted symbol. Rereads for narrower scopes, exact verification,
RED/GREEN tests and repaired Map builds are distinguished from redundant repeats
in the [independent report](benchmarks/2026-10-10/benchmark-combined-evaluation.md).

## Learning and second-run verification

Both first consumers independently reproduced the empty-file noninitial-range
false-success and proposed the same minimal `max(1, len(lines))` bound. Builder
Learning accepted `finding.2026-10-10.527f6d`; its
[owner-schema record](benchmarks/2026-10-10/learning-finding.json) is persisted.
The actual regression failed before the builder correction and passed afterwards,
with initial empty-file success explicitly preserved. Consumer Learning records
and complete/none owner closeout are retained in all final receipts.

Independent runtime-only checks on the **actual installed copies** found v1
correct in 4/6 held-out cases and v2 correct in 6/6. The two changed outcomes
reject empty-file ranges 2–3 and 4–7. Initial empty range, Unicode/U+2028/CRLF/tab
source and whole-file hashes remain correct. Fresh B2's installed context reader
passed all six, with native byte verification; A2's native route also passed six.
Both coding-task local CLIs preserved the two pre-fix failures and passed all six
after the same minimal change. Tests and held-out fixture bytes were unchanged.

This proves the bounded quality fix persists through governed learning,
implementation, isolated installation and fresh consumption. It does **not**
prove that default use of the toolset improves overall completed-task cost. B used
more traced calls and took longer overall; general productivity remains INCONCLUSIVE.

## Reproduction, release evidence and follow-up

[Machine-readable evidence](benchmarks/2026-10-10/benchmark-combined-evaluation.json),
raw traces, complete results, prompts, oracle, held-out bytes and SHA-256 manifests
are checked in under `docs/benchmarks/2026-10-10`. The earlier artifact named
`benchmark-installed-v1-v2-independent-heldout.json` used checkout executables;
its raw argv disclose that. The later `benchmark-actual-installed-v1-v2-independent-heldout.json`
verified real installed copies. Both are preserved, without relabeling earlier data.

The release includes a verified Git bundle for the exact task-baseline commit,
reproducible source archive, checksum manifest and final commit/CI metadata. Clone
the bundle into separate consumer directories, reproduce the documented dirty/
untracked/ignored fixtures from the receipts, and initialize approved Loop tasks
in fresh sessions using the saved prompts with local paths substituted. Fixture
reproduction does not reproduce model decisions or timing. Normal installation
uses a trusted Git checkout at a full commit SHA; a source tarball alone lacks
the Git provenance required by the installer.

Remaining limitations: small sample and synthetic PHP fixtures; unavailable
model-token telemetry; same-host timing; Git inventory coordinate ergonomics;
focused mutation coverage; private-prefix exclusive-access threat model; no
Windows installer contract; unverified cloud snapshot restoration. Follow up with
larger real PHP/static-analysis tasks, standardized command accounting, available
model telemetry and further independently measured cases before proposing any
default agent-loop integration. Repository source and retrieved CLI output remain
untrusted evidence throughout.
