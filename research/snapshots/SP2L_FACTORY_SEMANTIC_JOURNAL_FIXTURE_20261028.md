# SP2L Factory Incremental Snapshot — Semantic Journal Conflict Fixture — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-SEMANTIC-JOURNAL-FIXTURE-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Implementation commit: `e42b597520103b9e2f78884b7314770ec7d9e44f`
- Scope: one missing semantic-conflict regression fixture; no runtime or strategy behavior changed.

## Prior snapshots and tests checked to avoid duplicate work

Reviewed the existing snapshots:
- `research/snapshots/SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md`
- `research/snapshots/SP2L_FACTORY_LIFECYCLE_PROVENANCE_AUDIT_20261028.md`
- `artifacts/factory/SP2L_FACTORY_SNAPSHOT_20261007.md`
- `research/SP2L_STARNET_ENGINE_INTEGRATION_SNAPSHOT_20261007.md`

Reviewed existing tests:
- `tests/test_factory_test_journal_isolation.py`: catches implicit persistent journal use by tests.
- `tests/test_factory_worker_journal_audit.py`: already covers corrupt/missing/unreadable journal handling, byte-preserving file audits, deterministic worker/journal conflicts, and no automatic action.
- `tests/test_factory_holdout_forward_e2e.py`: already covers synthetic Fresh Holdout → Forward handoff/session/lifecycle/reconciliation identity binding and production lock.
- `src/strategy_factory/job_events.py`: parser validates JSON/schema/fingerprints/sequence; `recovery_summary()` already classifies invalid lifecycle sequences.
- PR #334 contains an append-transition guard on its own unmerged head; do not duplicate that implementation or assume it is present on the base.

## New narrow regression

Added `test_file_audit_flags_semantic_duplicate_terminal_without_mutating_journal` to `tests/test_factory_worker_journal_audit.py`.

The fixture constructs a temporary synthetic JSONL journal with valid per-record fingerprints and contiguous sequence but an invalid lifecycle:
`QUEUED → DISPATCHED → COMPLETED → COMPLETED`.

Assertions verify:
- structural journal integrity remains `VALID`;
- semantic audit returns `REVIEW_REQUIRED` and `JOB_LIFECYCLE_CONFLICT` for the exact job;
- repeated audit results are deterministic;
- `automatic_action_performed` remains false;
- source bytes are identical before and after the audit.

This deliberately does not modify or read the user's historical runtime journal. It is a synthetic regression only.

## CI

Both required workflows completed successfully on implementation commit `e42b597520103b9e2f78884b7314770ec7d9e44f`:
- Factory Research Tests — run #1090 — SUCCESS.
- SP2L forensic deterministic checks — run #636 — SUCCESS.

## Remaining blockers / next bounded step

- Historical runtime journal anomaly remains untrusted and unresolved; this fixture does not identify the historical writer or reconcile old events.
- Persisted append guard PR #334 remains open/unmerged; review its diff against current Factory base before deciding whether to port or rebase, and avoid duplicate implementation.
- The existing Fresh Holdout→Forward E2E test already checks handoff fingerprint, dataset artifact/hash, session/lifecycle identity, strategy/manifest revision, execution semantics, post-Holdout tuning false, and production decision false. Do not recreate that E2E test. Next provenance work should inspect missing negative cases: a stale/mismatched dataset or code/strategy identity across handoff/session/gate, and whether the public entry points fail closed.
- No production gate or statistical validation is approved by this synthetic test.

## Safety statement

No canonical SP2L geometry, strategy parameters, raw datasets, historical journals, runtime files, MT5 state, Strategy A RR2/TRAIL4 forward test, or Strategy B forward test were changed. No PR was merged; no production BUY/SELL decisions were generated.
