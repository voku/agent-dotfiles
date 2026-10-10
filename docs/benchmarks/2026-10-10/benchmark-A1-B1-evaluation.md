Independent A1/B1 evaluation

Both revised consumers returned complete, correct investigation evidence and the same minimal one-line Python fix. All existing tests remain byte-identical to baseline. Independent verification passed 58 Python tests and 6 Bashunit tests (13 assertions) for each consumer, plus six explicit source-range cases. Consumer traces themselves omitted the AGENTS-required Bashunit command; this is a validation-process omission, remedied by independent checks rather than erased.

The oracle was frozen before reading either result or trace, from native Git/source at commit 33003d8dc5f52c77c02d353804db0c04345f6f27 and fixture scripts. Oracle SHA-256: 74e6d10163b1a637d6cdbcce08e524523fcb6e8704687fd6687aeeaa76bd8013. Each complete patch matches its declared format byte-for-byte: A1 native abbreviated index, 206 bytes, c97bc8220843878e2e67d86c4410343e97529d3ec256b10c4cf0f5e88f3ab17d; B1 full-index, 272 bytes, d6ba8213574da5b27d7ebe13d6472b3e3b83c003e34c0337848195a68168f28d. Both contain only literal config/settings[1].ini.

Both identify Billing\PriceCalculator::total at src/Billing/PriceCalculator.php:4 and the two supported static callers Checkout.php:5 and Preview.php:5, verify source, and preserve dynamic/unsupported uncertainty. Both give nearest rounding at config/billing.yaml:2 and templates/receipt.twig:1, correct historical commit/paths, both individual untracked work files, and ignored-file exclusion with a separate exact read. Literal fixtures do not prove runtime invoice loading.

Inventory coordinate handling is correct in both results. A1 native Git from selected src emits paths relative to src. B1 tool emits repo-relative src/* while reporting selected root src; B1 records that fact and reads from repository root. Both return all 50 note bytes, preserving tab, embedded LF filename, U+2028 and absent final newline; whole-file SHA-256 is 3f6ac2c270d3b28fec9d9097ed3eaec1c51646b0c8d66121ad4a1a0cd8f83131. B1's root field alone remains ambiguous as a tool ergonomics concern, but its consumer did not make a path error.

Both initial receipts correctly disclose failed fresh Map analysis (child PHP lacked Phar) and blocked Learning storage/closeout. Root supplied equal PHPRC wrapper repair and the recognized Learning findings child directory; revised receipts preserve earlier failures and report owner-verified complete/none after a fresh Map with 4 files, 12 relations, zero diagnostics. Initial and revised results must be interpreted separately. The revised findings retain historical failure text, so that text is not evidence of current unavailability.

Timing and retrieval accounting

| Metric | A1 | B1 |
|---|---:|---:|
| All trace records | 50 | 64 |
| Initial / revised records | 39 / 11 | 50 / 14 |
| All-record elapsed sum | 13.73 s | 21.56 s |
| Leaf records after nested-parent exclusion | 50 | 57 |
| Leaf elapsed sum | 13.73 s | 14.97 s |
| Initial session wall time, approximate | 167.4 s | 161.9 s |
| Total session wall time including repair/wait, approximate | 297.5 s | 309.3 s |
| Strict redundant same-scope evidence retrieval count | 0 | 1 |

Seven B1 Python container records include separately traced children. All-record elapsed sums double-count their intervals; leaf sums remove containers. A1 Python scripts execute some direct native subprocesses within one record, so leaf counts are not a standardized count of every underlying process. Session starts were recorded just before spawns, not precise agent execution starts; end epochs are printed in raw consumer receipts. No rerun start timestamp exists, so no isolated rerun wall time is claimed. Model tokens are unavailable. Output bytes cannot stand in for them.

Both repeated RED/GREEN test runs and initial/repaired Map builds are necessary validation rather than redundant retrieval. A1 switches a contaminated bracket pathspec to literal selection and then binds the patch/hash; those narrower and verification calls are justified. B1's log then exact commit show narrows historical evidence, and native full-index comparison independently verifies its tool patch. B1 repeats exactly the same src inventory (trace22/31) without a source change; it helps bind the unusual name to its subsequent read, but it is still one repeat of already obtained evidence. Governance help/schema repair commands are outside the retrieval metric. The full JSON report provides command indices and more context.

A1 initially fetched the unrelated settings1.ini patch, detected contamination and corrected final evidence. Its full history included the earlier fixture commit. B1 initially listed the entire small repository and its nested receipts duplicated output. Neither revised receipt omits required task context. Reading Legacy code supports disambiguation and is useful.

This first trial demonstrates task completion and evidence integrity in both arms. It does not demonstrate overall efficiency improvement from the candidate: B1 has more raw and leaf records and greater traced elapsed sums; first-result wall time is slightly lower but revised total wall time is higher. Same-host concurrent work, fresh but different agents, small synthetic PHP fixtures, and shared prerequisite repairs prevent causal speed conclusions. The genuine Python empty-file regression adds a coding check without making this representative of a large production PHP application. No model-token or generalized productivity saving is claimed.

Detailed evidence: benchmark-A1-B1-evaluation.json; benchmark-A1-B1-independent-tests.json; benchmark-A1-B1-independent-range-validation.json. Independent held-out fixtures/oracle and task addendum for A2/B2 were separately frozen before those consumer directories or results existed.
