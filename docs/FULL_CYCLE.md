# Full-cycle evidence — 2026-10-10

**The tested empty-file range correctness improvement is PROVEN. Overall
productivity improvement is INCONCLUSIVE.** This historical experiment predates
the Bash/Zsh profiles; no new efficiency claim is made for shell helpers.

## Results

Four fresh governed agents used identical starting repositories and the same
agent-loop toolset. All completed investigations correctly, with no missing
required context in their final evidence. Optional tooling was slower overall
in this small comparison. Model-token telemetry was unavailable.

| Metric | Baseline A1 | Consumer B1 | Baseline A2 | Consumer B2 |
| --- | ---: | ---: | ---: | ---: |
| Final required evidence correct | yes | yes | yes | yes |
| Missing required context | 0 | 0 | 0 | 0 |
| Redundant same-scope retrievals | 0 | 1 | 0 | 2 |
| Approximate session time, seconds | 297.5 | 309.3 | 149.0 | 190.2 |

Both initial consumers found a false-success for noninitial ranges in empty
files. Governed Learning led to a minimal range-bound fix. Independent checks
on actual installed copies improved from 4/6 to 6/6 held-out cases; a second
fresh consumer retained the improvement. Initial empty reads, exact source bytes
and whole-file hashes remained correct.

## Immutable evidence

Generated payloads belong outside the current source layout. The original
report, raw receipts, fixtures, oracle, dependency/source manifests and release
artifacts remain accessible at their original immutable commits:

- [Complete original report and limitations](https://github.com/voku/agent-dotfiles/blob/d158e6c821cdae8064ac7b3817a0dd282236f842/docs/FULL_CYCLE.md)
- [Independent evaluation and raw benchmark evidence](https://github.com/voku/agent-dotfiles/tree/d158e6c821cdae8064ac7b3817a0dd282236f842/docs/benchmarks/2026-10-10)
- [v0.3.0 release](https://github.com/voku/agent-dotfiles/releases/tag/v0.3.0)
- [Original checksummed release artifacts](https://github.com/voku/agent-dotfiles/tree/17b238a3d4652371226df09126479a8d6e0628a6/docs/releases/v0.3.0)

Release source is `d158e6c821cdae8064ac7b3817a0dd282236f842`.
Builder agent-loop source was `622c004e2cc642fce1c06dc63a4f04d4889637e2`;
all consumers used `15507c3a313693eed45e2b1c98eda9c3aae7a7ef` (0.20.64).
The source/dependency manifests in the historical evidence record remaining pins.

PRs [#4](https://github.com/voku/agent-dotfiles/pull/4),
[#6](https://github.com/voku/agent-dotfiles/pull/6),
[#8](https://github.com/voku/agent-dotfiles/pull/8),
[#10](https://github.com/voku/agent-dotfiles/pull/10) and
[#11](https://github.com/voku/agent-dotfiles/pull/11) integrated the original work.
Python 3.10/3.12/3.13, macOS and Bashunit checks passed on their recorded commits.
Focused mutation testing killed 49/51 mutants, with two probable equivalent
string comparisons; this is not exhaustive installation mutation coverage.

Limitations: two comparison pairs, synthetic PHP fixtures, one shared host,
approximate timing, unavailable token telemetry, nonuniform trace accounting,
and prerequisite repairs. Larger real workloads remain tracked in
[issue #12](https://github.com/voku/agent-dotfiles/issues/12). Do not infer token
savings from output size or claim a general productivity benefit from these data.
