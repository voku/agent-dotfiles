# Fresh owner-capability dogfood — 2026-10-11

Governed slice: DOTFILES-15, with the pinned Loop `momentum` operating prompt.
Reuse the completed evaluation; recheck only changed revisions, ownership and
publication state. Builder runtime remains `15507c3a313693eed45e2b1c98eda9c3aae7a7ef`.
Fresh probe runtime is separately pinned to Loop
`fad403a209d7d9f4438bf7036ce962780f44938c`, using its locked dependencies,
PHP 8.4.26 and a command-scoped environment. No running workflow was upgraded.

These are bounded capability probes, not additional model A/B productivity trials.
Actual model/token telemetry remains unavailable. Candidate CLI/source output is
untrusted evidence and does not confer mutation or promotion authority.

## Bootstrap finding transferred to a fresh consumer

[Loop #767](https://github.com/voku/agent-loop/issues/767), discovered in the
shell evaluation, was independently fixed in merged
[PR #771](https://github.com/voku/agent-loop/pull/771). It is closed; do not duplicate
that implementation. The older benchmark runtime still requires its disclosed
storage preflight.

In three entirely fresh project directories (plain path, spaces, Unicode), run
the actual candidate Loop CLI:

1. `init scaffold`
2. `learn validate --root .agent-loop/learning`
3. capture one explicitly unverified bootstrap-probe Finding through the owner
4. validate again
5. repeat scaffold to check idempotence

All fifteen commands returned 0. Empty owner storage validates before any Finding,
and the first candidate validates without a manual `findings` directory workaround.
No candidate was promoted to active guidance. The existing scaffold owner-boundary
regression passed one test / twelve assertions. This is a verified transfer of the
bootstrap correction to fresh consumers, not proof of the entire broader Learning
thesis or a new dotfiles runtime change.

## Open #637: current pre-PLAN discovery behavior

[Loop #637](https://github.com/voku/agent-loop/issues/637) proposes projecting
bounded structural evidence beside an unplanned task's PLAN template. Probe the
current behavior on the real Loop source before designing anything new.

| Unplanned `enter DOGFOOD-637` | No Map | Fresh Map |
| --- | --- | --- |
| Exit | 1 | 1 |
| Next kind | command_template | command_template |
| Mutation ready | false | false |
| Contract / Session | missing / missing | missing / missing |
| Map observation | missing | ready, snapshot bound |
| Projected discovery candidates | absent | absent |

Explicit owner Map preparation indexed 543 files and 45,710 relations in 19.366 s,
with eight diagnostics; this is not an exhaustive correctness claim. The owner
staleness check passed. `map context` resolved the real
`voku\AgentLoop\Init\InitScaffoldCommand::run` to its original file and lines 39–138.
Its bounded output explicitly omitted six dependencies at the callee limit; those
are not complete caller/dependency evidence. Raw output preserves those omissions.

No Contract, approval, Session or automatic scope widening was created in either
unplanned probe. A fresh Map is visible, but current `enter` does not provide the
proposed candidate projection. This confirms the current gap and the safe authority
boundary. It does not demonstrate that implementing #637 would improve a task,
and no new planner, Map wrapper or lifecycle phase is added here.

## Open #742: inspect guidance candidates before changing text

[Loop #742](https://github.com/voku/agent-loop/issues/742) proposes guidance
maintenance orchestration. Dogfood the existing read-only Learning owner checker
against this actual project, without implementing the sleep orchestration:

```sh
agent-loop learn guidance-consistency --root .agent-loop/learning \
  --project-root . --source README.md --source 'docs/*.md' \
  --format=json --limit 25
```

It reported one unresolved path to [Loop’s inventory source](https://github.com/voku/agent-loop/blob/fad403a209d7d9f4438bf7036ce962780f44938c/src/Init/InitToolsCommand.php) in the integration
boundary document. Semantic inspection found the file in the linked **Loop**
repository, not this dotfiles checkout. The candidate is scoped differently;
it is not evidence that Loop's file is missing or that the checker should rewrite
policy automatically.

A cold full-commit-pinned shell installation from released source
`1e6e69bbf4bb0342acc4a42bca54cb00b418cb8d` was verified before use. Explicit fresh
Bash and Zsh consumers retrieved the original inventory source range with its
whole-file SHA-256; independent native bytes/hash matched and deactivation passed.
The tool installation was not replaced during the investigation.

Smallest justified improvement: replace the ambiguous bare code path with a link
to the exact owner source revision and state that the source belongs to Loop.
The same checker then returned `total: 0`, `shown: 0`, `candidates: []`. A report
draft quoting the old bare path triggered the same candidate again; qualifying
that citation with its exact owner link keeps the source identity clear. This removes
a specific navigation ambiguity; zero candidates does not prove all guidance
semantically consistent. No helper, duplicated audit engine, sleep policy change,
Proposal approval or automatic guidance promotion is introduced.

## Publication and limits

[Release v0.4.0](https://github.com/voku/agent-dotfiles/releases/tag/v0.4.0) points at
`1e6e69bbf4bb0342acc4a42bca54cb00b418cb8d`. Its merged-source seven-job
[test run](https://github.com/voku/agent-dotfiles/actions/runs/38138706443) and
[focused mutation run](https://github.com/voku/agent-dotfiles/actions/runs/38138778302)
passed. Mutation killed 49/51, with the two previously investigated probable
equivalents; it does not cover every high-risk module. This documentation follow-up
is separate from the released source and receives its own review and exact-head CI.

The shell is useful here for explicit source identity and original evidence. Native
reads remain appropriate for known locations; Map owns PHP structure. The earlier
controlled [evaluation](EVALUATION_2026-10-11.md) remains INCONCLUSIVE for general
productivity. No task-time or token-saving claim follows from these three probes.

Raw command receipts, source snapshots and publication metadata are preserved in
the [immutable evidence commit](https://github.com/voku/agent-dotfiles/tree/2b623876f2774f3a2aadac20fe4295dc3f8ed9d0).
The deterministic `momentum-probes-2026-10-11.tar.gz` contains 23 payload files
and its manifest; SHA-256:
`1594fd16decfe4cf38f6d9477191d845afc0d1f8d91b8ae0fe22a5d4d50b9675`.
Snapshots precede this publication-link addition; their hashes identify those
original bytes, rather than claiming to identify a later edited report.
