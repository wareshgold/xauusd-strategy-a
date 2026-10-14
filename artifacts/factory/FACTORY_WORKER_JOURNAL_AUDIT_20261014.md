# Factory worker journal audit snapshot — 2026-10-14

## Purpose and evidence boundary

This is a research/governance record of the read-only Factory worker/journal audit performed on 2026-10-14. The runtime observations below were reported from the user's local Factory worktree; the raw runtime files were **not** fetched from GitHub and are **not** included in this commit. This document records the reported audit output, not an independently reproduced inspection of those local bytes.

The audit is diagnostic only. It does not replay jobs, retry work, rewrite history, mutate worker state, or change strategy/production eligibility.

## Result

**Overall: REVIEW REQUIRED. Do not treat the current worker snapshot and main journal as a reconciled lifecycle record.**

Reported main-journal integrity:
- Status: `VALID`
- Event/line count: 128
- Byte size: 65,874
- SHA-256: `9c5953091dbed3b1c6ffb1516b64a9177f71c174914332eab9cd7956d226a9a8`
- SHA-256 before/after the audit was reported identical; journal unchanged.
- Worker snapshot was also reported unchanged. Its hash was not included in the available audit summary.
- Automatic action performed: `false`

A valid file hash establishes byte-level integrity for the inspected snapshot; it does **not** establish that its events form a valid lifecycle.

## Findings

### 1. `DISCOVERY-1` — repeated terminal lifecycle

- 122 journal rows, lines 7–128, all marked `COMPLETED`.
- Reported event timestamps span `2026-10-10T06:46:45Z` through `2026-10-11T10:56:36Z`.
- Each row has a distinct event fingerprint, while all rows share the same job fingerprint (`a1b5e054…`) and research-run fingerprint (`4e68019c…`).
- Audit finding: `LIFECYCLE_CONFLICT_REVIEW_REQUIRED`.

Interpretation: this is an invalid single-job lifecycle history requiring investigation. The repeated job/run fingerprints and distinct event fingerprints do not, by themselves, prove malicious tampering or explain how the rows were produced.

### 2. `JOB-EVENT-001` — conflicting terminal outcomes

Six reported rows for one job fingerprint (`b1bff04e…`):

1. `QUEUED` — `2026-10-10T06:32:16.631357Z`
2. `DISPATCHED` — same timestamp
3. `COMPLETED` — `2026-10-10T06:32:16.646965Z`
4. `QUEUED` — `2026-10-10T06:32:16.672246Z`
5. `DISPATCHED` — `2026-10-10T06:32:16.678284Z`
6. `FAILED` — same timestamp as row 5

Audit finding: `TERMINAL_CONFLICT_REVIEW_REQUIRED`. The history records both a completed and failed terminal outcome for the same job identity. Do not choose one outcome automatically.

### 3. `E2E-SYNTH-001` — worker snapshot/journal mismatch

The main journal reportedly contains no lifecycle rows for `E2E-SYNTH-001`, while `runtime/factory_worker_status.json` reports worker `W01` assigned to that job in state `FAILED`, with error `execution adapter failed` and publication time `2026-10-10T07:02:07.781881Z`.

Audit finding: `TERMINAL_WORKER_JOURNAL_MISMATCH`. The worker snapshot's reported last-write time is older than the main journal tail, so the files may represent different points in time; that is a possible explanation to verify, not a conclusion.

### 4. Separate synthetic journals are not a reconciliation

Two other runtime journals reportedly each contain a four-event sequence ending in `HANDOFF_ACCEPTED`:
- `runtime/factory_synthetic_e2e_job_events.jsonl`, job `SYNTH-E2E-20261011T050649014899Z`, SHA-256 `3f08dafa…`.
- `runtime/factory_synthetic_e2e_job_events_20261011_144721.jsonl`, job `SYNTH-E2E-20261011T111721954637Z`, SHA-256 `b120a76a…`.

These are different job IDs in separate files. They do not supply the missing `E2E-SYNTH-001` history in the main journal and must not be used to silently reconcile it.

## Code review status

The current branch already contains read-only audit logic in `src/strategy_factory/worker_journal_audit.py` and focused lifecycle tests in `tests/test_factory_worker_journal_lifecycle_history.py`. The code deliberately surfaces repeated/conflicting terminal lifecycle records even when the current worker snapshot does not reference the job, and does not repair the history.

The local Factory suite was reported as **811 passed** on the current worktree. GitHub Actions completed successfully for the initial audit snapshot commit: **Factory Research Tests** (run 577) and **SP2L forensic deterministic checks** (run 349). The subsequent change only updates this document to record those results; no workflow run was returned yet for that follow-up commit. These CI results validate the configured checks on the tested commit; they do not independently inspect the user's local runtime files or resolve the lifecycle findings.

## Required next actions

1. Preserve the original local runtime files unchanged. Do not delete, normalize, replay, rewrite, or auto-repair these histories.
2. Before any operational remediation, make a separately named, read-only evidence copy of the exact journal and worker snapshot; record both hashes, byte sizes, line counts, and capture times. Do not add runtime evidence or account/terminal data to Git by default.
3. Trace the writer/producer path for `DISCOVERY-1` and `JOB-EVENT-001`: find where terminal events are appended, whether a job identity is reused across repeated dispatches, and whether separate runs share the same journal. Use synthetic tests to reproduce the suspected lifecycle failure without editing the observed evidence.
4. Resolve the time/snapshot relationship for `E2E-SYNTH-001` and identify the authoritative source for the current worker state. Keep this unresolved until evidence establishes it.
5. Add a regression test for the specific producer defect only after the mechanism is demonstrated; then run focused and full tests. Any new journal/session should be a new artifact, not a rewritten version of this history.
6. Keep Factory readiness, frozen geometry, canonical Strategy Engine, and production eligibility unchanged. The existing readiness snapshot remains BLOCKED; this audit does not resolve source questions or authorize trading.


## Source trace — current GitHub branch (2026-10-14)

The following producer/consumer paths were inspected on `research/xauusd-availability-integrity-gate-20261013`:

- `src/strategy_factory/job_events.py`: a persisted `FactoryJobEventLedger` reloads the journal and validates the complete per-job lifecycle before each append. Its permitted sequence is `QUEUED → DISPATCHED → (COMPLETED | FAILED)`. A second terminal event for the same `job_id` is rejected before the file append.
- `src/strategy_factory/orchestrator.py`: `submit()` rejects a job ID already in the in-memory queue or ledger; `run_next()` writes `DISPATCHED` before execution and then appends one terminal event. The completion append is outside the executor `try/except`; if persisting `COMPLETED` fails, the worker can be terminal while the journal remains at `DISPATCHED`, which the existing audit intentionally leaves for manual reconciliation. This path explains a worker/journal mismatch, not 122 persisted `COMPLETED` events.
- `tests/test_factory_job_events.py`: the existing `test_ledger_rejects_repeated_completion_before_persisting` reconstructs a ledger from disk, attempts a second `COMPLETED`, and asserts the journal bytes are unchanged. Existing parameterized tests also reject invalid lifecycle transitions. Therefore a new duplicate-completion test would be redundant.
- `scripts/run_factory_synthetic_e2e.py`: explicitly refuses the live worker-status and main journal paths, refuses existing output files, and generates a unique synthetic run ID for isolated output. It is not an intended producer for the reported main-journal history.
- `scripts/run_sp2l_factory_discovery_mt5.py` / `src/strategy_factory/discovery_factory.py`: this real research Discovery path calls the research runner directly; the inspected path does not append lifecycle events to `runtime/factory_job_events.jsonl`.
- `scripts/factory_starnet_world.py`: reads the main journal to render handoffs; it does not append lifecycle events.

### Source-trace conclusion

Git history adds an important timing clue:

- The latest reported `DISCOVERY-1` event time is `2026-10-11T10:56:36Z`.
- Commit [`71196fb`](https://github.com/wareshgold/xauusd-strategy-a/commit/71196fb9bd48d9da9e41507e462720b7265576f6), titled `fix(factory): enforce job lifecycle transitions and audit conflicts`, was committed at `2026-10-11T11:03:19Z` — 6 minutes 43 seconds after that reported latest event time. Its commit record explicitly describes the then-observed repeated `DISCOVERY-1` completions and adds persisted-ledger transition enforcement.
- Commit [`a39674b`](https://github.com/wareshgold/xauusd-strategy-a/commit/a39674b47f553d42f7abac311ecedabf6c42035b), at `2026-10-11T11:06:46Z`, then scoped strict transition enforcement to persisted journals so in-memory synthetic/imported-history fixtures could still classify intentionally invalid histories.

This chronology strongly supports that the repeated completions were already present before the current persisted-ledger guard was introduced, rather than demonstrating that the current guarded append path is still emitting them. It does **not** identify which command or process wrote every row, and it does not explain the separate `JOB-EVENT-001` conflicting terminal sequence. Those remain historical evidence to preserve, not a reason to rerun the old writer.

The current inspected code and regression tests already guard against repeated terminal writes through a persisted ledger. The local journal's 122 `COMPLETED` rows therefore cannot be attributed to the inspected current persisted-ledger path without additional evidence. Plausible unresolved possibilities include historical rows written before the guard existed, a producer that bypassed the persisted ledger, or a different runtime code revision/path. These are hypotheses, not findings.

No additional code patch is justified yet: the existing repeated-completion regression already covers the invariant, and changing it without identifying the actual writer risks masking the source of the evidence. The next discriminating evidence is the exact runtime command/process or script that appended to the main journal at the reported timestamps, plus the relevant source revision then in use. Preserve the original files; do not run the writer against them to reproduce the anomaly.

The two configured GitHub Actions checks for the latest documentation commit completed successfully: Factory Research Tests (run 581) and SP2L forensic deterministic checks (run 351). They validate the configured checks, not the provenance of the local journal.

## Explicit non-conclusions

- No evidence here proves deliberate tampering.
- A valid SHA-256 does not mean the lifecycle is valid.
- The separate successful synthetic runs do not validate the conflicting main journal.
- No source geometry, entry/exit rule, canonical rule, or live trading decision is inferred or changed.
