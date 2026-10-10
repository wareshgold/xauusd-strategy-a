# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Latest user-verified baseline

- Latest user-verified baseline is commit `78c13ffb` on `research/factory-candidate-lab-20261010`.
- User-verified run after commits `a414a12c`, `6cd27e2b`, and `78c13ffb`:
  - Focused dispatch/recovery/lifecycle suite: **49 passed in 1.67s**
  - Full suite: **748 passed in 5.38s**
- The focused run includes `tests/test_factory_orchestrator_dispatch_boundary.py` and `tests/test_factory_orchestrator_process_interruption.py`.
- Subsequent commits `c430f7b9`, `458e6a39`, and `6d3599bc` record the verified baseline and add a submit-telemetry fault isolation fix/test. **These subsequent code/test changes are pending local validation.**
- Preserve the five untracked runtime/cache paths listed below.
- Preserve the five pre-existing untracked runtime/cache paths listed below.

Focused command just confirmed by the user:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_recovery_audit_integration.py tests/test_factory_recovery_report.py tests/test_factory_recovery_planner.py tests/test_factory_recovery_apply.py tests/test_factory_worker_journal_audit.py -q
```

Full suite just confirmed by the user:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

## 2. Preserve the user's working tree

Last user-reported status:
```
## research/factory-candidate-lab-20261010...origin/research/factory-candidate-lab-20261010
?? runtime/factory_demo_status.json
?? runtime/factory_job_events.jsonl
?? runtime/factory_worker_status.json
?? src/strategy_factory/__pycache__/
?? tests/fixtures/__pycache__/
```

Preserve these untracked runtime/cache artifacts. Do not clean, reset, stage, or commit them.

## 3. Completed Factory engineering

- Append-only lifecycle journal; telemetry publication faults isolated from job outcomes.
- Recovery report is deterministic and read-only; interrupted dispatched jobs require manual reconciliation.
- Queue reconstruction is split into explicit planning and separately approved application. Planning does not mutate queues or execute jobs; applying a plan does not dispatch it.
- Journal integrity reads one immutable byte snapshot, hashes and validates that same snapshot, and avoids second-read TOCTOU inconsistencies.
- Missing/unreadable/invalid journals fail closed as `REVIEW_REQUIRED`; no repair, truncation, replay, retry, or implicit requeue.
- Dashboard exposes a read-only Job Journal Integrity panel with status, counts, path, SHA-256 and findings; valid, missing, unreadable and invalid states have coverage.
- Demo telemetry remains separate from live worker telemetry. Forward Runner behavior is out of scope.

## 4. Integration test commits

### Confirmed by user
Commit `bf5bee4f`: `test(factory): integrate recovery report and journal audit`

File: `tests/test_factory_recovery_audit_integration.py`

The queued-only synthetic fixture checks report determinism, journal hash integrity, no automatic action, and unchanged journal/worker state.

Commit `ed5a9e75`: `test(factory): cover recovery lifecycle matrix integration`

File: `tests/test_factory_recovery_lifecycle_matrix_integration.py`

The parameterized matrix checks QUEUED-only, interrupted DISPATCHED, terminal COMPLETED, terminal FAILED, and conflicting terminal histories. It asserts deterministic recovery summaries, correct lifecycle classification, no automatic requeue/action, and unchanged journal bytes and worker state. User confirmed the containing recovery/lifecycle suite passed as part of **42 focused tests**, with **746 tests passing** in the full suite.

## 5. Mandatory guardrails

Do not change Forward Runner behavior, Holdout → Forward boundary, certified Holdout SHA semantics, Forward dataset identity, frozen strategy revision, or post-Holdout tuning prohibition.

Do not invent Strategy A geometry, entry/exit/fill semantics, P-Gap formula, AB=CD anchors/tolerance, or F12 touch/penetration/close semantics. Production BUY/SELL authority remains prohibited for AI.

Canonical workflow:
**SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.**

Passing engineering tests does not prove a statistical edge or authorize production.

## 6. Immediate next action

The process-interruption and worker-start dispatch boundary are now user-verified locally (**49 focused / 748 full**). Commit `a414a12c` removes the in-memory queue entry immediately after durable `DISPATCHED`, before worker startup; commit `6cd27e2b` verifies that a startup fault does not execute or redispatch the job and recovery reports `INTERRUPTED_REVIEW_REQUIRED`. These changes are validated by the reported test runs; they do not establish a trading edge or production readiness.

**Latest pending change — submit telemetry fault isolation:** after `QUEUED` is durably journaled and the in-memory queue updated, a failing `fleet.publish()` previously propagated out of `submit()`. That could make a caller believe submission failed and retry an already accepted job. Commit `458e6a39` routes this telemetry attempt through the safe publication recorder, and commit `6d3599bc` adds a synthetic regression test. The job remains queued; the publication error is recorded as `publish_after_submit`. **Pending user validation; do not call it verified until tests pass locally.**

Pull the latest branch, inspect the log/status, run the focused journal-fault and dispatch/recovery tests, then the full suite. Preserve all five untracked paths:
```powershell
git pull --ff-only
git log -6 --oneline
git status --short --branch
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_orchestrator_journal_faults.py tests/test_factory_orchestrator_dispatch_boundary.py tests/test_factory_orchestrator_process_interruption.py tests/test_factory_orchestrator_journal_faults.py tests/test_factory_recovery_lifecycle_matrix_integration.py tests/test_factory_recovery_audit_integration.py tests/test_factory_recovery_report.py tests/test_factory_recovery_planner.py tests/test_factory_recovery_apply.py tests/test_factory_worker_journal_audit.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```
