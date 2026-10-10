# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Exact resume point

- Latest branch head after the new integration regression: `bf5bee4f4d973e3540623ddd28ff2ef019c42f20`.
- The user-confirmed baseline immediately before this new test was `df7e3176ec7d6fe9f6db742be60ce91bde7cf4ed`.
- User-confirmed results at that baseline:
  - Focused dashboard/journal/orchestrator tests: **59 passed in 1.44s**
  - Full suite: **739 passed in 5.76s**
- A new integration regression was then added in `tests/test_factory_recovery_audit_integration.py`; **it has not yet been run locally**. The branch must not be described as green at `bf5bee4f` until the user runs it.

Focused baseline command:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_dashboard.py tests/test_factory_job_events.py tests/test_factory_worker_journal_audit.py tests/test_factory_orchestrator_journal_faults.py -q
```

Full suite:
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

## 4. New integration regression — pending local validation

Commit: `bf5bee4f` — `test(factory): integrate recovery report and journal audit`

File: `tests/test_factory_recovery_audit_integration.py`

The test joins the existing worker/journal integrity audit with deterministic recovery reporting for a synthetic queued-only journal. It checks that:
- both views agree on the journal event count;
- the integrity SHA-256 matches the original bytes;
- repeated recovery reports have identical content and identity;
- a queued-only job remains `QUEUED_REVIEW_REQUIRED`;
- no automatic requeue/action occurs;
- journal bytes and worker state remain unchanged.

This is a test-only change. No Strategy A rules or runtime execution paths were changed.

## 5. Mandatory guardrails

Do not change Forward Runner behavior, Holdout → Forward boundary, certified Holdout SHA semantics, Forward dataset identity, frozen strategy revision, or post-Holdout tuning prohibition.

Do not invent Strategy A geometry, entry/exit/fill semantics, P-Gap formula, AB=CD anchors/tolerance, or F12 touch/penetration/close semantics. Production BUY/SELL authority remains prohibited for AI.

Canonical workflow:
**SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.**

Passing engineering tests does not prove a statistical edge or authorize production.

## 6. Immediate next action

Pull the latest commit and run the new test, the focused regression set, and the full suite. Preserve the five untracked paths above. If any test fails, share the complete output before making further changes.

```powershell
git pull --ff-only
git log -5 --oneline
git status --short --branch
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_recovery_audit_integration.py tests/test_factory_recovery_report.py tests/test_factory_recovery_planner.py tests/test_factory_recovery_apply.py tests/test_factory_worker_journal_audit.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

The **59 focused / 739 full** results are confirmed for `df7e3176`, not for the new integration-test commit. Record fresh counts only after local execution.
