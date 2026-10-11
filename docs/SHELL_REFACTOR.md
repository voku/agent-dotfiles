# Modular shell preflight follow-up (DOTFILES-25)

Baseline: `8f2e22801285419d93d7bb29bef4bd198bea1bda`.
The requested module organization arrived in PRs #26 and #29 while this task
was underway; PRs #28, #31, #32 and #33 added installer planning and independent
workspace consumers. This follow-up preserves that integrated work rather than
replacing it with a competing structure. Public entry points, module inventory,
installer manifests, CLI behavior and dependencies remain unchanged.

Independent review demonstrated that `[ -r module ]` accepts a directory.
Bash then continued after a failed source operation, exported the tool root and
reported successful activation with missing helpers. Installed manifest verification
already refuses such directories, but explicit development-checkout activation
needed the same boundary. Entry points and activation now require regular files
before sourcing assets or accepting the executable. Actual Bash/Zsh tests replace
each required asset with a directory and assert status 2, a diagnostic, no stdout,
no tool-root export and none of the public helpers. Existing unusual-path,
namespace-collision, missing-file and reversible-lifecycle tests remain intact.

The task runs under the unchanged independent agent-loop builder
`15507c3a313693eed45e2b1c98eda9c3aae7a7ef`, approved Contract revision 2.
An initial structural candidate was preserved locally before synchronization;
its test evidence does not validate this newer baseline or final candidate.
Fresh validation and CI are required on the final commit.

Previous findings in [full cycle](FULL_CYCLE.md),
[evaluation](EVALUATION_2026-10-11.md) and [quality cycle](QUALITY_CYCLE_17.md)
remain relevant: optional consumers were correct but sometimes slower and needed
repeated retrieval. This fix proves a lifecycle correctness boundary, not a
productivity or token benefit. Dream must review this observation alongside
previous dogfood evidence. Generated candidates are not approved guidance, and
zero evaluated guidance with unknown outcome coverage is not proof of quality.
No release, default activation or unreviewed host customization is authorized.
