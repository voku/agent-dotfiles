# ADR 0002: Keep reviewed workflow knowledge in the project repository

- Status: Accepted as storage convention; host/runtime verification pending
- Date: 2026-10-12
- Context: Existing `agent-loop` and `agent-learning` owners, and the absence of project-owned memory on this checkout

## Decision

Maintain `MEMORY.md` as a short index of **durable reviewed rules**, and `docs/decisions/` as human-readable decision records. Configure a project-local `.agent-loop/learning` root following the current upstream format. Review and commit validated owner-produced findings selectively; ignore raw sessions, history, generated context, checkpoints, and caches. Do not replicate agent-loop workflow state here.

A successful coding task does **not** automatically turn observations into rules. Required sequence: collect evidence in the governed run, use actual Learning-owner validation and review, decide whether a durable change exists, update the canonical code/test/decision, and only then update memory. Memory never grants approval.

## Verification and risk

The files in this slice are scaffolding. A real installed agent-loop consumer still must prove that the configured root is accepted and findings are emitted to that root. Until that proof exists, do not claim automated persistence or successful governed closeout. Repository maintainers must inspect every tracked finding for credentials, private conversation data and unsupported recommendations before merging.
