# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-10  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`

## 1. Exact resume point

- Latest branch head verified on GitHub: `df7e3176ec7d6fe9f6db742be60ce91bde7cf4ed`.
- The user has confirmed local HEAD/origin sync at this branch state.
- Most recent user-confirmed tests, after pulling the latest dashboard Journal edge-case tests:
  - Focused: **59 passed in 1.44s**
  - Full suite: **739 passed in 5.76s**
- These are engineering/regression results only. They do **not** establish a profitable trading edge or authorize Strategy A production.

Focused command used:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_dashboard.py tests/test_factory_job_events.py tests/test_factory_worker_journal_audit.py tests/test_factory_orchestrator_journal_faults.py -q
```

Full suite:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

## 2. Preserve the user's working tree

The last user-reported `git status --short --branch` was:
```
## research/factory-candidate-lab-20261010...origin/research/factory-candidate-lab-20261010
?? runtime/factory_demo_status.json
?? runtime/factory_job_events.jsonl
?? runtime/factory_worker_status.json
?? src/strategy_factory/__pycache__/
?? tests/fixtures/__pycache__/
```

These untracked runtime/cache artifacts must be preserved. Do not clean, reset, stage, or commit them.

## 3. Completed Factory engineering

### Job lifecycle and recovery evidence
- Append-only lifecycle journal records declared Factory job transitions.
- Telemetry publication failures are isolated from the actual job outcome.
- Completion/failure journal faults remain visible as reconciliation findings; no automatic repair is attempted.
- Recovery summaries expose lifecycle provenance and identify conflicts between the journal and worker snapshot.
- Replay submission is explicit and validates the original journaled failure; recovery inspection must not implicitly replay jobs.

### Journal integrity and audit
- Journal inspection reads one immutable byte snapshot, computes SHA-256, validates that same snapshot, and can construct an in-memory ledger from the validated events without a second read.
- Valid, missing, unreadable, invalid, truncated, invalid-UTF-8, and changing-snapshot edge cases have regression coverage.
- Missing/unreadable/invalid journals fail closed as `REVIEW_REQUIRED`; there is no partial ledger, repair, truncation, replay, retry, or write.
- Audit findings are diagnostic only and do not authorize a job or strategy decision.

### Read-only dashboard
- Factory dashboard includes a Job Journal Integrity panel with audit status, integrity status, event/finding counts, path, SHA-256, and findings.
- Valid/consistent states and review-required states have distinct severity.
- Missing, unreadable, invalid, and valid journal states have dashboard tests.
- Rendering the panel does not dispatch jobs, recover/retry work, or mutate the journal.
- Demo telemetry remains separate from live worker telemetry. Do not alter Forward Runner behavior as part of this work.

## 4. Guardrails that remain mandatory

This branch is Factory engineering and research governance only. Do not change:
- Forward Runner or live/demo trading behavior without a specifically scoped request.
- Holdout → Forward boundary, certified Holdout SHA, separate Forward dataset identity, frozen strategy revision, or post-Holdout tuning prohibition.
- Strategy A geometry, entry/exit/fill semantics, or execution rules.
- Production BUY/SELL authority. AI must not autonomously generate production trade decisions.
- Unresolved P-Gap formula, AB=CD anchors/tolerance, F12 touch/penetration/close semantics, or other unresolved source meaning.

Canonical workflow:
**SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.**

Source meaning outranks backtest performance. Passing engineering tests is not proof of a statistical edge and is not permission to start formal Demo Forward from the Factory.

## 5. Next engineering step

### Controlled post-restart Recovery Inspection — read-only first

The next task is to make the restart/recovery state explicit and auditable, without changing runtime behavior:

1. Define a deterministic, read-only recovery inspection report from existing journal lifecycle evidence and worker snapshot.
2. Explicitly classify queued-but-not-dispatched, dispatched/interrupted, terminal, conflicting, and incomplete-journal cases only where the current recorded evidence supports those distinctions.
3. Add synthetic contract tests for restart-like states and assert no queue mutation, no worker mutation, no journal writes, no executor calls, and no automatic retry/replay/requeue.
4. Keep inspection separate from any future operator-approved recovery action. If evidence is incomplete or contradictory, return review-required rather than guessing.
5. Run focused tests and the full suite locally; only then update this snapshot with the new verified SHA/results.

Do not infer missing lifecycle events, reconstruct a queue from assumptions, or silently rerun interrupted work. This step must not introduce new Strategy A rules or affect Holdout/Forward gating.

## 6. Resume / verification commands

```powershell
git pull --ff-only
git log -5 --oneline
git status --short --branch
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_dashboard.py tests/test_factory_job_events.py tests/test_factory_worker_journal_audit.py tests/test_factory_orchestrator_journal_faults.py -q
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

Preserve all five untracked runtime/cache paths listed above. The **739 passed** result is confirmed for `df7e3176`; any new code must be tested again before calling the branch green.
