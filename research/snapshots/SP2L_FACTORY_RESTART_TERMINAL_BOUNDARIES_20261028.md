# SP2L Factory Snapshot — Restart Recovery at Terminal Event Boundaries — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-RESTART-TERMINAL-BOUNDARIES-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Test commit: `5a931f1e5e0f31b4a9f3558e5ca7e8f0cd008b2b`
- Scope: synthetic restart/recovery behavior at the boundary before and after durable terminal journal persistence.
- Status: added tests and Factory Research CI passed; SP2L deterministic CI passed; journal-lock matrix passed on Ubuntu and Windows. This snapshot records software/evidence integrity only, not a trading-edge result.

## Added tests

File: `tests/test_factory_restart_terminal_boundaries.py`

1. `test_restart_after_executor_return_but_before_terminal_journal_is_review_only`
   - Synthetic executor returns a result, then terminal `COMPLETED` append raises `SystemExit`.
   - The in-process worker has reached `COMPLETED`, but the durable journal remains `QUEUED, DISPATCHED`.
   - A newly loaded ledger reports `INTERRUPTED_REVIEW_REQUIRED`.
   - Recovery does not mutate journal bytes and `automatic_requeue_performed` remains false.

2. `test_restart_after_durable_terminal_event_does_not_mark_job_interrupted`
   - Synthetic interruption is injected after durable `COMPLETED`, at the post-completion telemetry boundary.
   - A newly loaded ledger reports `TERMINAL_COMPLETED`.
   - The journal remains `QUEUED, DISPATCHED, COMPLETED`; no automatic requeue or journal mutation occurs.

All test inputs are synthetic. No MT5, forward-test process, Strategy A geometry, canonical SP2L rules, or production authorization was touched.

## CI verification on test commit

- Factory Research Tests: PASS — run `40668903500`
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40668903500
- SP2L forensic deterministic checks: PASS — run `40668903554`
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40668903554
- Factory Journal Lock Cross-Platform Tests: PASS — run `40668903532`
  - Ubuntu: PASS
  - Windows: PASS
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40668903532

Verification is CI-based; no local test execution is claimed.

## Interpretation and limits

- A durable `DISPATCHED` without a durable terminal event remains ambiguous and requires manual review, even if process-local state had reached a terminal state.
- A durable `COMPLETED` event is recognized as terminal on restart even if post-completion telemetry is interrupted.
- These tests verify the current journal-derived recovery contract. They do not prove executor side effects are transactionally exactly-once; the ambiguous pre-terminal boundary must not be silently retried.
- No journal repair, automatic retry, or historical rewrite was introduced.
- No PR was merged.
- No statistical trading edge, live execution safety, or production readiness is inferred.
