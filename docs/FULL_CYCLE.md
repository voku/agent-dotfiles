# Historical full-cycle evaluation (v0.3.0)

The complete original report is preserved in the
[immutable Git snapshot](https://github.com/voku/agent-dotfiles/blob/17b238a3d4652371226df09126479a8d6e0628a6/docs/FULL_CYCLE.md).

Raw traces, initial/final consumer receipts, SHA-256 manifests and held-out
oracles remain in the
[historical benchmark tree](https://github.com/voku/agent-dotfiles/tree/17b238a3d4652371226df09126479a8d6e0628a6/docs/benchmarks/2026-10-10).
The
[original release artifacts](https://github.com/voku/agent-dotfiles/tree/17b238a3d4652371226df09126479a8d6e0628a6/docs/releases/v0.3.0)
are retained in that same commit rather than duplicated in active source.

The installed file-reader held-out correctness improved **4/6 to 6/6**;
that bounded fix is proven within the test set. General productivity remains
**inconclusive**: optional agents took longer overall and token telemetry
was unavailable. This historical evaluation does not establish default
agent-loop adoption.
