# Factory Lifecycle Audit — 2026-10-11

## Scope

Factory orchestration diagnostics only. This audit does not modify runtime telemetry, replay jobs, change Strategy A geometry, certify a candidate, or authorize production decisions. Forward Runner is out of scope.

## Observed local runtime evidence supplied for review

- Main journal: `runtime/factory_job_events.jsonl`
- Snapshot: `runtime/factory_worker_status.json`
- Journal integrity was reported as `VALID` with 126 events and no exact duplicate event payloads.
- `DISCOVERY-1` accounts for 120 `COMPLETED` lifecycle records, with contiguous global sequence values 7–126, distinct timestamps and distinct event fingerprints, but the same job fingerprint and research-run fingerprint.
- The recovery summary classifies this history as `LIFECYCLE_CONFLICT_REVIEW_REQUIRED`. This is a lifecycle-contract conflict, not proof that the event rows are byte-level duplicates.
- The worker snapshot describes `E2E-SYNTH-001` as `FAILED`, while no lifecycle event for that job exists in the main journal. The consistency audit therefore requires manual review.
- The independent synthetic E2E journal was reported `CONSISTENT` (4 events). It is a separate journal and does not reconcile the main-journal mismatch.

## Change in this branch

The read-only worker/journal audit now emits an explicit finding for journal lifecycle histories classified as either:

- `LIFECYCLE_CONFLICT_REVIEW_REQUIRED`
- `TERMINAL_CONFLICT_REVIEW_REQUIRED`

This finding is emitted even when the current worker snapshot contains no row for the conflicted job. Previously the recovery status count could expose the conflict, but the findings list could omit it if no worker row triggered a mismatch. No automatic repair or retry was added.

## Follow-up prevention change

The append API now validates new lifecycle transitions against the history loaded by the ledger. It accepts only `QUEUED`, `QUEUED → DISPATCHED`, and `QUEUED → DISPATCHED → COMPLETED|FAILED`; duplicate transitions and any lifecycle append after a terminal event are rejected before persistence. Non-lifecycle handoff markers remain separate. This prevents sequential process restarts from appending another terminal event to a job whose terminal state is already present. It does not retroactively alter or repair the observed runtime journal, and it is not a cross-process file-lock guarantee; concurrent writers would need separate coordination if the Factory is ever run concurrently against one journal.

## Local validation requested

Run from the repository root after pulling this branch:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_factory_worker_journal_lifecycle_history.py tests/test_factory_worker_journal_audit.py tests/test_factory_job_events.py
```

Then run the full suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Explicit non-actions

- No runtime JSON/JSONL files were changed or cleaned.
- No job was retried or replayed.
- No worker state was rewritten.
- No Strategy A geometry, execution semantics, candidate ranking, holdout, or production gate was changed.
- No Forward Runner files were changed.
- Local validation of the prior audit-only branch passed (51 targeted tests and 761 total). This follow-up append guard and its added/adjusted tests have not yet been run locally; run the targeted and full suites after pulling this branch.
