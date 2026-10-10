# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Latest user-verified baseline

- Latest user-verified baseline is commit `cd6e3199` on `research/factory-candidate-lab-20261010`.
- User-verified run at that baseline:
  - Focused dispatch/recovery/journal-fault suite: **50 passed in 1.59s**
  - Full suite: **749 passed in 5.21s**
- The focused run includes the submit-telemetry fault regression test.
- Subsequent commits `fa35b20c` and `b5a4e54f` isolate handoff telemetry publication faults and add a synthetic regression test. **These latest code/test changes are pending local validation.**
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

The user has verified submit telemetry fault isolation (**50 focused / 749 full**) at `cd6e3199`. Commits `458e6a39` and `6d3599bc` ensure that once `QUEUED` is durable and the in-memory queue is updated, a telemetry publication fault is recorded as `publish_after_submit` rather than escaping and encouraging a duplicate submission.

**Latest pending change — handoff telemetry fault isolation:** `HANDOFF_ACCEPTED` is journaled before telemetry publication. If `fleet.publish()` fails, propagating the error could make the caller treat an already accepted handoff as unsuccessful. Commit `fa35b20c` routes the publication through the safe telemetry recorder, and `b5a4e54f` adds a synthetic regression test asserting the durable handoff remains returned and the telemetry fault is recorded. **Pending local validation; do not call it verified until tests pass locally.**

Pull and run the focused suites, then the full suite. Preserve the five untracked paths:
```powershell
git pull --ff-only
git log -6 --oneline
git status --short --branch
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_orchestrator_handoff_telemetry.py tests/test_factory_orchestrator_journal_faults.py tests/test_factory_orchestrator_dispatch_boundary.py tests/test_factory_orchestrator_process_interruption.py tests/test_factory_recovery_lifecycle_matrix_integration.py tests/test_factory_recovery_audit_integration.py tests/test_factory_recovery_report.py tests/test_factory_recovery_planner.py tests/test_factory_recovery_apply.py tests/test_factory_worker_journal_audit.py tests/test_factory_handoff.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```
