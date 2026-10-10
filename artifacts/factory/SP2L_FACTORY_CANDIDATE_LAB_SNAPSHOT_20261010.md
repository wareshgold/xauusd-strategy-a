# SP2L Factory Candidate Lab — Handoff Snapshot
**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Exact resume point

Latest user-confirmed local state:
- `HEAD` and `origin/research/factory-candidate-lab-20261010` are aligned at `a6a2d701`.
- Last five commits:
  1. `a6a2d701` — `test(factory): cover file integrity in worker journal audit`
  2. `746ac12e` — `feat(factory): include journal integrity in worker audit`
  3. `199c748e` — `feat(factory): expose immutable journal snapshot for audits`
  4. `f89b76bb` — `test(factory): make journal fixture newline unambiguous`
  5. `e20114bc` — `test(factory): write real newline in invalid event fixture`

### User-confirmed test results
- Focused regression:
  ```powershell
  & "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_job_events.py tests/test_factory_worker_journal_audit.py tests/test_factory_orchestrator_journal_faults.py -q
  ```
  **50 passed in 1.08s**
- Full suite:
  ```powershell
  & "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
  ```
  **732 passed in 5.44s**
- These are the user's reported local results at commit `a6a2d701`. Do not imply any newer code has been tested until the user runs it.

### User-confirmed working-tree status
```
## research/factory-candidate-lab-20261010...origin/research/factory-candidate-lab-20261010
?? runtime/factory_demo_status.json
?? runtime/factory_job_events.jsonl
?? runtime/factory_worker_status.json
?? src/strategy_factory/__pycache__/
?? tests/fixtures/__pycache__/
```
These untracked runtime files and cache directories are intentionally preserved. Do not clean, delete, mass-add, or commit them.

## 2. Completed in the current Journal/Audit hardening sequence

### Journal integrity inspection
- `78f30cae` — `feat(factory): add read-only journal integrity inspection`
  - Adds `inspect_job_journal_file(path)`.
  - Reports statuses including `VALID`, `MISSING_REVIEW_REQUIRED`, `UNREADABLE_REVIEW_REQUIRED`, and `INVALID_REVIEW_REQUIRED`.
  - Reports file metadata and SHA-256; explicitly states `automatic_repair_performed=False`.
  - No repair, truncation, or write.
- `3808a851` — tests valid journal, truncated tail preservation, missing vs valid-empty file, invalid UTF-8 preservation.
- `0cd7270c` — makes invalid UTF-8 test bytes explicit.
- `75f8e7cd` — fixes truncated-tail fixture to start with a valid event before the malformed second line.
- `c3e27d55` — preserves validation error detail and adds line number.
- `a29fe099` — tests event validation line diagnostics and byte preservation.
- `e20114bc` and `f89b76bb` — repair the test fixture newline encoding issue. The final fixture uses `chr(10)`, ensuring an actual newline; user confirmed tests passed afterward.

### Orchestrator telemetry fault isolation and recovery evidence (earlier in this branch)
- `4e4cfeb3` — telemetry publication failures are isolated from job execution.
- `fecfc1da` — tests dispatch/heartbeat telemetry failures.
- `919b5841` — preserves completed job result if final telemetry publication fails after durable completion.
- `08fc6a54` — completion/telemetry fault tests.
- `fa1d7ce2` — recovery summary exposes lifecycle provenance fields.
- `39b777cb` — recovery provenance tests.
- `67eb01e4` — corrects interrupted event sequence assertion.
- `69912516` — joins recovery summary with worker snapshot and reports `RECOVERY_WORKER_STATE_CONFLICT`.
- `6e584e96` — tests recovery/worker conflicts and no mutation/action.

## 3. Latest implementation at `a6a2d701`

### `src/strategy_factory/job_events.py`
- Adds `inspect_job_journal_snapshot(path)`, which reads raw bytes once, calculates SHA-256, decodes/validates that exact snapshot, and returns:
  - an integrity report; and
  - parsed immutable event tuple if valid, otherwise `None`.
- `inspect_job_journal_file(path)` delegates to this snapshot inspector and returns the public report.
- Adds `FactoryJobEventLedger.from_snapshot(events)` to construct an in-memory ledger from already validated events, avoiding a second file read (TOCTOU mismatch) during file audit.
- Validation errors retain line-number detail. Invalid source bytes remain unchanged.

### `src/strategy_factory/worker_journal_audit.py`
- Adds `inspect_worker_journal_file_consistency(workers, path)`.
- It inspects integrity and audit events from the same validated byte snapshot.
- If the journal is missing, unreadable, or invalid, it fails closed:
  - overall status `REVIEW_REQUIRED`;
  - finding `JOURNAL_INTEGRITY_REVIEW_REQUIRED`;
  - no partial ledger is used;
  - no repair/replay/retry/write is performed.
- If valid, it runs the existing read-only worker/journal consistency audit against an in-memory ledger built from the validated snapshot and includes `journal_integrity` in the report.

### New tests in `tests/test_factory_worker_journal_audit.py`
- Valid on-disk journal includes integrity report and uses a stable snapshot.
- Corrupt journal requires review and preserves original bytes; no replay/repair.
- Missing journal requires review.
- Existing consistency/recovery conflict tests remain present.

## 4. Current scope and non-negotiable guardrails

This is Factory engineering and audit hardening only. Do not change:
- Forward Runner, live/demo runner, or dashboard behavior outside explicit scoped work.
- Holdout → Forward boundary, certified Holdout SHA semantics, distinct Forward dataset identity, frozen strategy revision, or post-Holdout tuning prohibition.
- Strategy A geometry or execution rules.
- Production BUY/SELL authority; AI must not generate production trade decisions.
- Any unresolved P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.

Canonical workflow:
**SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.**

Only source-confirmed rules can become canonical. Diagnostic/backtest outcomes do not decide source meaning. No formal Demo Forward should be started merely because these audit tests pass.

## 5. Next step — do not duplicate completed work

1. Pull latest branch only if remote has advanced; preserve all untracked runtime/cache artifacts.
2. Review the file-level audit implementation for edge cases (especially missing/unreadable paths and stable snapshot semantics); add focused regression tests where needed.
3. Run focused tests and the full suite with the known-good interpreter. Report only observed results.
4. If all tests pass, consider a separate, explicit integration point for exposing the file-level audit report to the Factory operator/dashboard. First trace the existing reporting path; do not wire it into orchestration in a way that can trigger retries, recovery actions, or job execution.
5. Keep this work on `research/factory-candidate-lab-20261010`; ask user to `git pull --ff-only` and test after GitHub commits.
6. Update this snapshot with the next verified state rather than creating duplicate plans.

## 6. Resume command

```powershell
git pull --ff-only
git log -5 --oneline
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_job_events.py tests/test_factory_worker_journal_audit.py tests/test_factory_orchestrator_journal_faults.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
git status --short --branch
```

**Snapshot truth rule:** this document records user-confirmed test results through `a6a2d701`. Any subsequent commit requires fresh local validation before it can be marked green.
