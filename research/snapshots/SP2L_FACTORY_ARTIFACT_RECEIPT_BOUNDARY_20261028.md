# SP2L Factory Snapshot — Artifact Receipt Reconciliation Boundary — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-ARTIFACT-RECEIPT-BOUNDARY-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Test commit: `8271493be3bc5542c9a6c2bfb15934f627ebc82f`
- Scope: synthetic restart-recovery contract when an artifact-related marker exists without a durable terminal lifecycle event.
- Status: Factory Research Tests PASS; Factory Journal Lock Cross-Platform Tests PASS on Ubuntu and Windows.

## Source audit finding

The current job journal validates each event fingerprint and records `output_artifact` as an identifier plus an optional `research_run_fingerprint`. Recovery's lifecycle classifier considers only `QUEUED`, `DISPATCHED`, `COMPLETED`, and `FAILED`. The research evidence model separately has an `evidence_fingerprint`, but the recovery summary does not resolve an artifact ID to an immutable evidence record or verify artifact bytes.

Therefore, this audit does not invent an artifact receipt protocol or infer completion from a filename, artifact ID, or non-lifecycle marker. A `DISPATCHED` job without a durable `COMPLETED`/`FAILED` lifecycle event remains `INTERRUPTED_REVIEW_REQUIRED` and requires manual reconciliation.

## Added synthetic test

File: `tests/test_factory_artifact_receipt_reconciliation_boundary.py`

`test_non_lifecycle_artifact_marker_cannot_promote_interrupted_job` appends `QUEUED`, `DISPATCHED`, and a synthetic `HANDOFF_ACCEPTED` marker carrying an artifact ID and run fingerprint, but no terminal lifecycle event. After reload, recovery remains `INTERRUPTED_REVIEW_REQUIRED`; no automatic requeue or journal mutation occurs.

The earlier test in `tests/test_factory_artifact_side_effect_interruption.py` also verifies that an artifact file written before interruption does not make the job replay-safe.

## CI on test commit

- Factory Research Tests: PASS — run `40669402324`
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40669402324
- Factory Journal Lock Cross-Platform Tests: PASS — run `40669402343`
  - Ubuntu: PASS
  - Windows: PASS
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40669402343
- SP2L forensic deterministic checks passed on the immediate parent snapshot commit `416f8ade41a9e03a80870399b58307b1042d67c0`; a separate fresh forensic run for this test commit was not observed.

Verification is CI-based; no local test execution is claimed.

## Limits and non-goals

- No durable artifact-receipt schema, artifact registry, or external-byte reconciliation protocol is implemented.
- This is a fail-closed boundary test, not proof of exactly-once external side effects.
- No automatic replay, queue reconstruction, journal repair, or artifact deletion was added.
- No MT5, Strategy A entry logic, unresolved SP2L geometry, production decision path, or live forward-test process was touched.
- No PR was merged.
- No statistical trading edge or production readiness is inferred.
