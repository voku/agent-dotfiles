# Governed shell maintenance evaluation — 2026-10-11

**General productivity improvement: INCONCLUSIVE.** First seeded maintenance and
real PHP diagnosis are independently graded; fresh held-out maintenance is complete and recorded below. A specific guarded activation invocation prevents false success.
Machine-scope failures invalidate earlier full-governance claims, even where
technical tests pass.

## Frozen versions and method

Baseline agent-dotfiles: `8bd0aa7172908f59b4e5e8031bb2afaafc9cc179`.
All consumers use agent-loop `15507c3a313693eed45e2b1c98eda9c3aae7a7ef`
with recorded Composer dependencies and PHP 8.4.26. Candidate shell revision:
`b9ea6199e9ca50d1168cc8257e03dfb792966157`.

Three fresh agents, identical inherited model settings, separate checkouts and
installation prefixes on one shared host. Isolation is instruction based, not an
OS security boundary. Agents run sequentially; setup and independent evaluation
may overlap. Actual provider model identifier and token telemetry are unavailable.
Wall time includes provider scheduling, review wait and governed closeout. Trace
receipts represent compound subprocess commands, not model tool-call totals.

The first task deliberately injects a whole-source digest regression in a private
seed (`05b2a8bd746c0d91eac3bff86b50d5812024c324`). Main already behaves correctly;
the experiment does not discover or repair a production digest defect. A private
independent oracle was frozen before consumers, and all repairs were independently
reviewed and graded. Existing and added regressions fail on the injected seed.

## First maintenance round

| Outcome | Native A | Standalone CLI B | Bash profile C |
| --- | ---: | ---: | ---: |
| Wall time, seconds | 161.884 | 192.213 | 168.467 |
| Independent correctness cases | 4/4 | 4/4 | 4/4 |
| Final required source context missed | 0 | 0 | 0 |
| Irrelevant context treated as relevant | 0 | 0 | 0 |
| Strict repeated identical retrievals | 0 | 0 | 0 |
| Avoidable optional post-discovery searches | 0 | 0 | 1 |
| Compound trace receipts | 21 | 27 | 25 |

All three reached Loop `complete/none`, independent review and session-bound
Learning; each passed 87 Python tests, compileall and 9 Bashunit tests/20 assertions.
However, their machine-approved Contracts scoped only `tests`, excluding the
implementation file they repaired. Root misunderstood `--file`: when `--scope`
is supplied, it replaces the file list as the allowed scope. These are technical
results, **not scope-compliant governed maintenance proof**. No retroactive
approval is claimed. Subsequent fresh Contracts explicitly include the source.
Repair commits are A `781f80283c0772f3193e5d833be2315211a6fdd9`,
B `f68b015875eabd50644998bfb417fe0a081260c0`,
C `655cfed87ede7756fa5244a2d940fec8e72a6188`.

B chose native bounded source reads, using the optional installed CLI only for
help. C performed a broad optional search after native discovery; its low limit
returned valid but irrelevant matches and omitted the implementation. The JSON
explicitly signalled incompleteness, but a later command masked exit 3. Native
evidence prevented a wrong result. Loop/Learning syntax and lineage discovery
accounted for additional friction; shell functions do not own those contracts.

## Validated learning and candidate

Choose native tools for known locations; use structured helpers when source
identity, exact literal scope or completeness matters. Scope discovery before
reducing output limits. Preserve each command status and inspect completeness.
The reviewed candidate documents this routing rather than adding more wrappers.
It also salvages shell validation from conflicting PR #14 in the current layout:
ShellCheck, Bash/Zsh syntax and required Linux runtime activation tests. Removing
an ignored Zsh argument and making empty CDPATH assignments explicit preserves
source resolution and shell state. A cross-range digest regression is retained.

Local candidate validation: 87 Python tests, compileall, 9 Bashunit tests/20
assertions, ShellCheck 0.10.0 and seven actual Bash/Zsh activation contracts pass.
Independent review also passed ShellCheck 0.11.0 and the activation contracts.
On candidate `b9ea6199e9ca50d1168cc8257e03dfb792966157`, GitHub
[test run 38099979660](https://github.com/voku/agent-dotfiles/actions/runs/38099979660)
and push run 38099965738 passed Python 3.10/3.12/3.13, macOS installation,
Bashunit and Linux shell contracts.
[Focused mutation run 38100001650](https://github.com/voku/agent-dotfiles/actions/runs/38100001650)
killed 49/51 validation-module mutants. Two surviving `==` to `is` comparisons
with the literal `"."` are probable equivalents on the tested CPython runtime;
no timeout or pending worker error. This is not mutation coverage of source
reading, installation or PHP maintenance.

The final local patch additionally preserves activation refusal with
`. "$1/.bashrc" || exit $?`, documents citation verification, and retains one
focused held-out separator regression. Main already has correct LF-only
segmentation: no injected repair is applied to production. Independent review
of this patch passed. Local final gates pass 88 Python tests, compileall and
9 Bashunit tests/20 assertions. These later edits are not validated by the older b9 checks. Core revision
`e41260137b0e2677307bbcb5b607a28718459080` independently passed
[test run 38120619478](https://github.com/voku/agent-dotfiles/actions/runs/38120619478),
push run 38120616832, and
[mutation run 38120641307](https://github.com/voku/agent-dotfiles/actions/runs/38120641307).
All supported Python, macOS, Bashunit and shell gates passed; focused mutation
again killed 49/51 with the same two probable equivalents and no pending/error
workers. This report-only addition receives a fresh final-head test run; merged
release-source checks and actual publication are linked from PR #16 / release
notes after completion, without claiming pending checks passed.

## Governance corrections

Root DOTFILES-12 also omitted root shell, installer, README and changelog paths
from its machine-approved scope. The user authorized those changes, but that
authorization does not establish compliance with the narrower recorded Contract.
The failure is checkpointed; correctly scoped DOTFILES-13 governs final review
and publication without widening the original Contract. PHP-A likewise added
a diagnostic outside its approved directory scope. PHP-B/C remain separately
audited.

The fresh held-out profile consumer detected the scope mismatch and paused
implementation mutation. Its r2 Contract included `agent_dotfiles/cli.py` and
`tests` before repair. The correction wait makes its wall time unsuitable for
a clean efficiency comparison. Native and CLI arms have corrected Contracts
before starting. The original held-out profile pilot is also excluded because
the root harness omitted owner-recognizable empty Learning storage.

## Limitations and remaining work

An excluded pilot used a root-assigned task ID rejected by Learning's identifier
contract. Its technical repair passed, but closeout was blocked. Preserve its
cost separately; it is not a valid baseline. All three balanced consumers were
restarted fresh with valid IDs. A/B bootstrap reads were untraced; C had no
untraced shell calls. Batched commands sometimes masked intermediate errors.
First-round traces lack absolute timestamps, so time to first evidence is unknown.
No token savings can be inferred from output bytes.

Second-round tracing adds absolute start timestamps. All three fresh consumers
receive the same scoped-tool guidance; cross-round timing differences therefore
cannot establish a tool-only causal effect. A separately frozen source-line task
provides held-out correctness checks. Real PHP workload uses actual Loop #761 /
PR #758 at `97e41c72539b95abf9636b25f551c20da683fbef`: bounded reproduction and
owner-safe diagnosis (S0) is distinct from a complete production fix or semantic
approval. Raw receipts are published outside the product tree at the immutable evidence
link below. Final-head CI, merge and release publication remain separate gates.

## Actual PHP maintenance: issue #761 / PR #758

Source snapshot: `97e41c72539b95abf9636b25f551c20da683fbef`.
Historical rejected change: base `622c004e2cc642fce1c06dc63a4f04d4889637e2`,
head `f1d1f7b91a7adad974aa88ca5104135894d43196`.
The bounded task (S0) reproduces the actual rejection and diagnoses owner-safe
next steps; it does not grant semantic approval or complete the production fix.
All arms found the required source and Learning owner boundaries, preserved the
negative gate, and passed independent S0 diagnosis. **Issue #761 remains
UNRESOLVED.** A passing reproducer is evidence of an open defect, not remediation.

| Outcome | Native PHP-A | CLI PHP-B | Profile PHP-C |
| --- | --- | --- | --- |
| S0 independent grade | PASS | PASS | PASS |
| Original + added diagnostic tests | 10 / 19 assertions | 10 / 18 assertions | 10 / 22 assertions |
| Full Composer CI | exit not captured | original exit 1 | captured exit 0 |
| Wall seconds | 309.184 | excluded, provider interruption | 398.288 |
| Final missing context / false relevance | 0 / 0 | 0 / 0 | 0 / 0 |
| Strict repeated retrievals | 0 | 0 | 0 |
| Approved machine scope | FAIL | PASS | PASS |

Repair/diagnostic commits:
A `3ea0ab07ae7da5940c116c3d8c0317e684fd3c30`,
B `fefb7a7f3758fff20a15e2939576777bdc8ef44b`,
C `2f8d8f95c959899973ab45aefbf6de68e779b002`.
PHP-B's measured wall includes hours of provider unavailability (20,840.335 s),
so comparable active/task time is unavailable. Its original full run passed
1,538 tests but failed the scanner on a historical fixture copied into the
checkout; moving its fixture outside source and rerunning the failed scanner
passed. This does not make the original full CI run successful. PHP-C captured
full CI exit 0 (1,538 tests / 10,382 assertions, one warning, deprecation and skip).
PHP-A's trailing log command lost the Composer exit: its completed test log is
insufficient proof of full CI success.

Root clarified an incorrectly prepared existing-test path after PHP-A and
external fixture handling after PHP-B. Consequently this is an exploratory
comparison, not a clean causal estimate. B/C initially misquoted source line
numbers; independent review corrected them before final grading. Those
review-driven rereads are justified retrievals, not redundant searches.
PHP-B used optional structured source reading; PHP-C chose native tools.
Learning owns validated proposal/target evidence; Loop must not infer approval
from private JSON, memory edits or an actor string. Diagnostic fixtures depend
on historical Git objects and are archived evidence, not shallow-clone-ready
production changes. No PHP diagnostic is merged upstream.

## Second fresh held-out maintenance

All arms receive the same frozen revised guidance and tracer-v2; treatment is
optional tool availability, not forced usage. Source seed:
`5a3c07549c501212e0a0c96f3da459a24b4cafb2` (an injected `splitlines` defect;
production main already correct). Frozen private oracle covers Unicode,
carriage-return-only and form-feed sources independently of implementer tests.
Candidate prefixes stay pinned to `b9ea6199e9ca50d1168cc8257e03dfb792966157`.

Native A2 `73bf948d59df9b67efa2da15728dc2f1a63b87e9` passed 3/3 held-out
cases, 88 Python / 9 Bashunit tests and canonical `complete/none` with run-bound
Learning. Approved source scope was correct before spawn. Wall 157.304 s,
29 compound receipts / 5 nonzero. First relevant compound receipt completed
25.334 s after root start; exact source read completed at 30.036 s. These are
output-availability bounds, not internal first-hit measurements. Final required
context missed, false relevance and strict repeated retrievals were all zero.

Profile C2-valid `5a51932bf809c4faad048dbecfb08a6b9811afa7` passed 3/3,
88 Python / 9 Bashunit tests and `complete/none` with current-run Learning.
It correctly stopped before modifying source excluded from its initial Contract;
root approved r2 source scope before repair. Its 495.873 s wall is confounded by
that correction wait (39 receipts / 14 nonzero). It chose native known-location
reads and did not activate the profile. First relevant receipt completion was
20.377 s; exact source read 27.287 s. Final missing context, false relevance and
strict repeats were zero. This validates the governance pause, not shell speed.
CLI B2 `863b667b2bcef475ca594d2bfcfcd38e2102ec30` passed 3/3,
87 Python / 9 Bashunit tests and `complete/none` with run-bound Learning.
Its r2 scope was correct before spawn. Wall 195.151 s, 32 compound receipts /
11 nonzero; first relevant completion 25.798 s and exact read 29.681 s.
Final missing context, false relevance and strict repeats were zero. It chose
native tools; optional CLI availability did not improve this known-location task.

Final fresh profile C2-final `cf893d9c1354eb101967988c3fa10f91e525104b`
passed 3/3 held-out cases, 87 Python / 9 Bashunit tests and `complete/none`.
Its r1 source scope and empty owner-recognized Learning storage were correct
before spawn. Wall 171.760 s, 28 receipts / 6 nonzero; first relevant receipt
completion 24.691 s and exact source read 29.160 s. Final missing context, false
relevance and strict repeats were zero. It selected native reads without profile
activation. This additional fresh trial follows A2/B2; the earlier C2 setup pilot
(286.982 s, also out of source scope) and C2-valid correction wait (495.873 s)
remain disclosed, not erased or cherry-picked as faster replacements.

| Clean held-out quality set | Native A2 | CLI B2 | Profile C2-final |
| --- | ---: | ---: | ---: |
| Independent correctness | 3/3 | 3/3 | 3/3 |
| Approved scope and Loop closeout | PASS | PASS | PASS |
| Final missing / false relevant / strict repeats | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Wall seconds | 157.304 | 195.151 | 171.760 |
| Optional tool actually used for evidence | absent | no | no |

Comparable task quality persisted in fresh correctly scoped sessions. The
optional availability treatments were largely unused; these numbers cannot prove
a CLI/profile causal productivity benefit. No default adoption is justified.

## Installation and narrow learning evidence

Two fresh Bash/Zsh consumer shells verified the immutable candidate manifest,
whole-file native hash, exact selected bytes and deactivation. Existing installer
and shell tests exercise cold private installation, verification, refusal of
unmanaged changes/symlinks, removal and prior-prefix rollback. The pinned Loop
starts and finishes native A2 without an installed optional toolset. No global
startup file, shell, PATH or Git configuration was changed by the product.

An independent activation fixture places a preexisting `agent_search` name in a
fresh shell. The old documented invocation ignores activation refusal, calls
that foreign helper and exits zero. The guarded invocation returns activation
exit 2 and does not call it. Separate missing-binary and missing-functions cases
retain exit 2 instead of falling through to exit 127. This invocation correction
is **PROVEN for those fixtures**. It does not demonstrate general productivity.

Root captured and validated current-session Finding
`finding.2026-10-11.fdf2bd` through Learning in correctly scoped DOTFILES-13.
Earlier Finding `finding.2026-10-11.70cbf8` and all failed/bootstrap attempts are
retained. Learning changes the scoped/status/citation guidance and adds measured
regression coverage; fresh consumers are free to use native tools. Zero extra
profile searches after guidance is consistent with the finding, but identical
all-arm guidance and small samples cannot establish tool-only causation.

## Remaining limitations and publication state

The canonical `init scaffold` succeeds but creates an empty Learning parent that
the Learning owner rejects. Independently reproduced at PHP source `97e41c...`;
an empty `findings` directory makes owner validation accept zero records.
Preflight uses this minimal storage correction without fabricated records.
The owner follow-up [Loop #767](https://github.com/voku/agent-loop/issues/767)
needs canonical init-to-Learning contract coverage, not a
weakened arbitrary-directory resolver. Explicit `--scope` semantics also need
clearer pre-implementation verification. These are Loop responsibilities.

Model input/output/cached tokens and exact provider model identity are unavailable;
no token savings are claimed. Raw failures, setup pilots, scope audit, source
pins, traces and private oracle grades must remain reviewable. General shell
adoption remains opt-in. At report preparation the published release is v0.3.0; source e412601
prepares version 0.4.0. Release publication is recorded separately when completed.
At continuation, GitHub temporarily returned HTTP 401 and Git could not
authenticate. A subsequent read-only retry succeeded without changing credentials
or verification. Final evidence/commit push, exact-final-head CI, merge, PR #14
disposition and next release are recorded only when completed. Existing green
b9 checks do not validate later edits.

Additional discovery source pins are retained in `repository-revisions.json`:
agent-map `9feade3b6edf43c772bda7eb3fe00e6ca323a757`; agent-learning
`d9b83da0a5a0388637a126c14bc9b509802b3b49`; agent-recall-compiler
`afc94971c35700c8b9f449368da347281752252f`; upstream dotfiles
`79333d8dda8131732e44574e0dc089a8b47f70cf`. Runtime dependencies are
separately pinned; these discovery revisions do not replace the frozen executable.

## Immutable experiment evidence

[Raw archive, checksums and reproduction instructions](https://github.com/voku/agent-dotfiles/tree/ecee21c253fc49fe6506b38497cddfa9d2fc81e6)
are on a dedicated evidence branch, outside the product layout. Archive SHA-256:
`7338426188b8363b20b7401d0ff89a5e3c0cee22fcfdca3f77ea6b8469225b28`. It contains 1,138 indexed payload files plus the manifest, including failed commands,
excluded pilots, owner states, source seed bundles, repair patches, private
oracles now unfrozen, independent grades and scope audit. Five large derived
structural indexes are omitted with hashes and reproduction pins; no trace or
grade is omitted. Two builds produced identical archive bytes.

Measured first-round and clean held-out consumer wall sums to 1,046.780 s
(522.565 + 524.215); PHP-A/C add 707.471 s. These are task-run sums, not total
project effort: prep, independent review, GitHub queue, excluded pilots and the
20,840.335-second provider-interrupted PHP-B run remain separate. Mission-wide
model resource accounting is unavailable. Output bytes are never token estimates.

Final reviewed core pin `e41260137b0e2677307bbcb5b607a28718459080`
passed cold installation, manifest verification, strict doctor, fresh Bash/Zsh
exact-byte/hash reads, deactivation, uninstall and previous b9 prefix rollback.
The earlier running benchmark prefixes remain unchanged.
