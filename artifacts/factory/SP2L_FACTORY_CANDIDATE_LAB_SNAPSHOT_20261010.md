# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Latest user-verified baseline

- User confirmed the latest process-interruption test commit is pulled and the local/origin branch is synced at `b9cbb3a9`.
- Latest verified run:
  - Orchestrator/recovery/lifecycle focused suite: **48 passed in 1.42s**
  - Full suite: **747 passed in 5.34s**
- These results include `tests/test_factory_orchestrator_process_interruption.py`.
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

The process-interruption case is verified locally (48 focused / 747 full). Inspection identified a dispatch boundary risk: `DISPATCHED` was persisted before `worker.start()`, while the in-memory queue entry was removed only after `worker.start()` returned. A start failure could therefore leave a dispatched job queued in the current process. Commit `a414a12c` moves queue removal immediately after durable `DISPATCHED`, before worker startup, so the same in-memory queue cannot redispatch it after a startup fault. Commit `6cd27e2b` adds `tests/test_factory_orchestrator_dispatch_boundary.py` to verify no execution, no second dispatch, and `INTERRUPTED_REVIEW_REQUIRED`. **Both changes are pending local validation**. Pull and run the focused boundary/recovery suites and then the full suite. Preserve the five untracked paths above.

```powershell
git pull --ff-only
git log -5 --oneline
git status --short --branch
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_recovery_lifecycle_matrix_integration.py tests/test_factory_recovery_audit_integration.py tests/test_factory_recovery_report.py tests/test_factory_recovery_planner.py tests/test_factory_recovery_apply.py tests/test_factory_worker_journal_audit.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

The latest user-confirmed counts are **48 focused / 747 full** at `b9cbb3a9`.
