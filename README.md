# Shell maintenance evaluation evidence, 2026-10-11

Raw failures, excluded pilots, exact source/dependency pins, consumer traces, owner contracts/run states, independent grades, machine-scope audit, activation proofs and targeted mutation diagnostics. Generated evidence is deliberately outside the product branch.

Verify `SHA256SUMS`, then extract the archive into a fresh directory. `MANIFEST.json` checks every payload file and documents five omitted derived structural indexes by hash. They can be regenerated with the pinned owner/source; no trace, result or oracle grade is omitted. Archive generation is deterministic (sorted entries, uid/gid/mode/time normalized, gzip time zero); a second build produced the same hash.

Private source seeds are now unfrozen after all consumers finished. Seed Git bundles require the public baseline commit `8bd0aa7172908f59b4e5e8031bb2afaafc9cc179`; import their `refs/evaluation/round1` or `round2` refs, then apply the appropriate consumer repair patch. Main already correctly handles both seeded defects. PHP diagnostics reproduce the actual PR #758 rejection, not a production fix for #761.

Read the per-arm independent grades and machine-scope audit separately: correct repairs and a completed workflow projection do not prove earlier out-of-scope edits complied with their Contracts. No retroactive approval. C2 pilot and C2-valid setup waits remain disclosed. Logical isolation shares one host; actual provider model identity and token telemetry unavailable.

Benchmark tool candidate: `b9ea6199e9ca50d1168cc8257e03dfb792966157`. Final reviewed product core/cold-install pin: `e41260137b0e2677307bbcb5b607a28718459080`. These are distinct and running consumers were not upgraded. Exact final CI, merged/released source and final owner closeout are recorded separately after completion; this snapshot is not release approval.

General productivity: INCONCLUSIVE. Guarded fresh-shell activation prevents false success in the independently reproduced cases. See agent-dotfiles PR #16 and docs/EVALUATION_2026-10-11.md for the readable report.

## Subsequent publication and momentum probes

PUBLICATION.json records the exact merged-source CI/mutation/release receipts and the correctly scoped parent closeouts; the original failure remains preserved. `momentum-probes-2026-10-11.tar.gz` with MOMENTUM_SHA256SUMS contains fresh bootstrap, current pre-PLAN and guidance-consistency probes plus actual pinned-shell source evidence. Source snapshots match worktree-read hashes before documentation publication links were appended. These probes do not prove general productivity or implement #637/#742 orchestration.

## Additional quality cycle (PR17 and fresh PHP repairs)

`quality-cycle-17.tar.gz` preserves 1,199 payload files plus a hash/byte manifest:
private-then-disclosed independent oracles, both seed bundles, six repair bundles,
actual command traces and raw owner contracts/session/review/Learning states.
First-round blockers and harness timeouts are retained. Source snapshots precede
the report publication-link append and DOTFILES18 closeout; those follow separately.
`QUALITY-CYCLE-17-REVIEW.json` is the independent report review. This is source/evidence
publication, not a release or active-guidance approval.
