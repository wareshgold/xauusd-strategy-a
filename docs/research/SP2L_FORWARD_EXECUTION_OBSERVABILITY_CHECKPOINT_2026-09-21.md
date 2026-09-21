# SP2L Forward-Test Execution Observability Checkpoint — 2026-09-21

## Status

Research-only. Canonical Strategy A and production remain disabled.

## Change

Commit `ea9ea66ad3eb3eef12a155fae6c180b3270efa37` adds explicit execution observability to:

`scripts/run_sp2l_author_replica_forward_test.py`

For every detected research candidate, the runner now records:

1. `CANDIDATE`
2. `TELEGRAM_SIGNAL`
3. `ORDER_ATTEMPT`
4. `ORDER_RESULT`
5. `ORDER_PLACED` or `ORDER_REJECTED`
6. existing `EXECUTION_MISS` when the theoretical entry is no longer placeable.

The audit records bid/ask, entry, SL, TP, volume, order mode, retcode/comment where available, and MT5 last-error state. No strategy geometry, price level, retry behavior, or canonical rule was changed.

## Important

The GitHub-side workflow list exposes no run for this commit, so CI is not claimed green here.

The actual MT5 order path still requires local execution against the user's demo terminal. No local order-placement test is claimed from GitHub.

## Required local verification

Run the forward runner with the existing demo-only environment flags and inspect the terminal output for:

- `ORDER_ATTEMPT`
- `ORDER_RESULT`
- `ORDER_PLACED` or `ORDER_REJECTED`

Then keep Telegram monitor running separately for deal-level confirmation.

## Guardrail

This change is execution observability only. It does not resolve F09/F10/F11/F12/F13 semantics and does not promote any research hypothesis to canonical Strategy A.
