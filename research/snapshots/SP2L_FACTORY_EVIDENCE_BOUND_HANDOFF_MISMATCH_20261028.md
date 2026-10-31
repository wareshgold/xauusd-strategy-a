# SP2L Factory Snapshot — Evidence-Bound Handoff Mismatch Regression — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-EVIDENCE-BOUND-HANDOFF-MISMATCH-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Test commit: `d17b8cf318ee77f891d8300a223c97e2014aad82`
- Scope: add one synthetic regression for the existing evidence-bound handoff contract. No production implementation was changed.

## Regression added

`tests/test_factory_handoff.py::test_handoff_rejects_completed_artifact_that_conflicts_with_research_record`

The fixture constructs a valid synthetic `ResearchRecord`, then supplies a `COMPLETED` source event whose `output_artifact` differs from the record's `evidence_id`, while retaining the matching run fingerprint. The handoff must reject the mismatch rather than route a conflicting artifact onward.

This test exercises the repository's already-declared contract:
- the handoff artifact must equal the research record's evidence ID;
- the source completion event must be bound to the same research run;
- a completion marker alone does not override inconsistent evidence identity.

It does **not** verify external artifact bytes, add a persistent artifact registry, or establish a generic output-artifact receipt protocol.

## CI on the exact test commit

All three observed checks passed on `d17b8cf318ee77f891d8300a223c97e2014aad82`:

- Factory Research Tests — PASS: https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40670629663
- Factory Journal Lock Cross-Platform Tests — PASS, Ubuntu and Windows: https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40670629595
- SP2L forensic deterministic checks — PASS: https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40670629833

## Boundary and next decision

The regression closes a narrow test-coverage gap in the existing handoff identity checks. The generic output-artifact byte-verification gap remains unresolved and must not be filled by guessing a schema. Before implementing durable receipts, obtain an approved contract for artifact ID/path mapping, serialization, digest computation, atomic publication, restart verification, and manual reconciliation.

Recovery remains fail-closed: an interrupted dispatched job without a durable terminal lifecycle event is not automatically completed or replayed based on an artifact identifier or file existence.

## Exclusions

No Strategy A geometry, P-Gap, AB=CD, entry/fill/execution rules, trading parameters, statistical claims, or production decisions changed. No MT5 terminal, Strategy A or Strategy B forward runner, local worktree, runtime file, or event log was touched. No pull, merge, cleanup, or automatic journal repair was performed.
