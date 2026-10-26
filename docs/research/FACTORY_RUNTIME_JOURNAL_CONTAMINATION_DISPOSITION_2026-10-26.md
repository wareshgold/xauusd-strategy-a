# Factory Runtime Journal Contamination — Disposition and Reconciliation Gate

**Status:** quarantined for research use; manual review required  
**Prepared:** 2026-10-26  
**Scope:** historical Factory runtime journal only. This document does not define SP2L geometry, trading rules, or production authority.

## 1. Decision

The historical journal is evidence that must be preserved, not a trusted source of current job state. Its JSONL records and fingerprints can be structurally valid while its lifecycle history is semantically contradictory.

Until a separately reviewed reconciliation is completed:

- Do not truncate, rewrite, delete, reorder, replay, auto-retry, or “repair” the historical journal.
- Do not infer that a job completed successfully from a `COMPLETED` row alone.
- Do not treat a worker snapshot as proof of a journal writer or as a substitute for lifecycle evidence.
- Do not use the journal as authority for current Factory job state, canonical SP2L rules, or production BUY/SELL decisions.
- Preserve the raw bytes, SHA-256, file metadata, audit output, and relevant Git commit IDs as separate evidence.

This is a quarantine disposition, not a claim that the historical writer has been conclusively identified.

## 2. Observed local artifact

The inspected Factory candidate-lab artifact was:

- Relative path: `runtime/factory_job_events.jsonl`
- Size: 71,064 bytes
- Last-write time reported: `2026-10-17T05:54:42.1659293Z`
- SHA-256: `A0AA59EEE4182B9C5D3E9ABA70863AF28050AF719EB354172BF716E2E48EF54C`
- Total records: 138
- Event-type counts: `COMPLETED=133`, `DISPATCHED=2`, `FAILED=1`, `QUEUED=2`

The journal was structurally parseable but failed semantic lifecycle review. These measurements identify the inspected snapshot only; any later file must be re-hashed and treated as a new snapshot.

## 3. Anomaly inventory

### 3.1 Repeated `DISCOVERY-1` terminal events

There are 132 `COMPLETED` events for `DISCOVERY-1`, sequences 7–138. They share the same job fingerprint, research-run fingerprint, worker `worker-1`, station `stability`, phase `STABILITY`, detail `Stability completed`, and output artifact. Their event fingerprints are unique.

The observed interval runs from `2026-10-10T06:46:45.305659+00:00` through `2026-10-17T05:54:42.151420+00:00`. This pattern is not evidence of 132 independent Stability executions.

### 3.2 Conflicting `JOB-EVENT-001` terminal history

Historical test source at commit `875db2eb` used implicit persistent ledgers in two tests that share the default job ID `JOB-EVENT-001`: one records a successful terminal event and another records a failed terminal event. This is a plausible synthetic-test source for a conflicting terminal history if that version ran against the affected checkout. The exact execution is not proven.

### 3.3 Worker snapshot mismatch

The separately observed worker snapshot names `E2E-SYNTH-001`, state `FAILED`, and a detail indicating it was queued for research execution. It does not match the repeated `DISCOVERY-1` events. The snapshot's timestamp and contents do not identify which process wrote the journal.

## 4. Source-supported explanation and confidence

The strongest supported explanation is historical test-fixture contamination:

- Commit [`875db2eb`](https://github.com/wareshgold/xauusd-strategy-a/commit/875db2ebda78c68ecea2700362b1347c8655b20e) used `FactoryJobEventLedger()` without an isolated path in the validation fixture and in two job-event tests.
- Commit [`97fc1e00`](https://github.com/wareshgold/xauusd-strategy-a/commit/97fc1e006903efaa7be5294bedd19675a7368e3e) changed the validation fixture to `FactoryJobEventLedger(path=None)` on 2026-10-11.
- Commits [`bc0c0f0b`](https://github.com/wareshgold/xauusd-strategy-a/commit/bc0c0f0bd03c0364e4ffbf2f99031d70694cac21) and [`5c9f6fe2`](https://github.com/wareshgold/xauusd-strategy-a/commit/5c9f6fe2167885d16a1367b54a8c49449d907274), at 06:26:38Z and 06:27:53Z on 2026-10-17, repeated/clarified the validation-fixture isolation change. The last observed journal event is timestamped about 32 minutes before the first of these commits.
- Commit [`0ee25b03`](https://github.com/wareshgold/xauusd-strategy-a/commit/0ee25b033c6579cbd6bfd08044cdd6088264ac71) added a static test to reject implicit persistent-ledger construction in tests.
- Merged PR [#351](https://github.com/wareshgold/xauusd-strategy-a/pull/351) changed `FactoryOrchestrator` so its default event ledger is in-memory (`path=None`) and added regression coverage to the focused Factory CI workflow.

**Confidence statement:** source history confirms that unsafe test code existed and was subsequently isolated. The timeline and repeated event shape fit contamination. The exact local process, checkout/ref, test invocation count, and row-by-row origin are unproven. In particular, the journal continued to receive matching events after the 2026-10-11 source fix, so a stale/alternate checkout or another writer remains possible.

## 5. Controls now present in source

The reviewed research branch contains:

- `tests/test_factory_test_journal_isolation.py`: rejects implicit persistent-ledger construction in test files.
- `tests/test_factory_orchestrator_default_journal_isolation.py`: asserts that default Orchestrator construction uses an in-memory ledger.
- `tests/test_factory_job_events.py` and `tests/test_factory_worker_journal_audit.py` included in the focused Factory test workflow.
- The Orchestrator's default ledger is non-persistent; persistence must be explicitly requested.

These controls prevent known recurrence paths; they do not retroactively authenticate or repair the historical journal.

## 6. Reconciliation gate — no automatic repair

Any future reconciliation must be a new, reviewable artifact and must not mutate the source journal. It should:

1. Capture the source journal bytes and SHA-256 before analysis; verify the hash again after analysis to detect accidental mutation.
2. Record the exact repository, branch/ref, commit SHA, Python executable, command line, working directory, and test invocation history available from logs. Mark unavailable fields as unknown rather than guessing.
3. Build an append-only, line-numbered anomaly table containing sequence, timestamp, job ID, event type, job fingerprint, research-run fingerprint, event fingerprint, worker, station, phase, detail, and output artifact.
4. Evaluate lifecycle ordering, duplicate terminal events, fingerprint drift, event-time ordering, and worker/journal disagreement separately. Structural validity must not be conflated with lifecycle validity.
5. Distinguish proven facts, source-supported hypotheses, and unresolved questions. Do not attribute an event to a process without direct evidence.
6. Require human review before producing any reconciled interpretation. Never overwrite the original file or silently turn a conflict into a successful terminal state.
7. Keep runtime/production authority disabled until the reconciliation is reviewed and a separate operational decision is recorded.

No test or worker execution is required to preserve this disposition. Do not run a Factory or trading runner as part of the historical investigation.

## 7. Acceptance criteria to close the investigation

The investigation can be closed only when either:

- direct logs or reproducible provenance identify the writer(s) and explain the observed rows; or
- the remaining attribution gap is explicitly accepted, the original snapshot is preserved, all recurrence controls are verified by CI, and the journal remains permanently marked as untrusted historical evidence.

Closure of this investigation does not establish canonical Strategy A geometry, statistical edge, or production readiness.
