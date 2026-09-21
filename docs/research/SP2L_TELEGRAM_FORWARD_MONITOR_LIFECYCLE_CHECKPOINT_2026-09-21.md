# Telegram Forward Monitor Lifecycle Observability Checkpoint — 2026-09-21

## Status
RESEARCH-ONLY / OBSERVABILITY HARDENING

## Change
Commit `7d506a37c0dae070b5901499bd5638cec4868700` hardens `scripts/telegram_forward_monitor.py`.

The monitor now:
- reports OPEN and CLOSE lifecycle events;
- identifies TAKE PROFIT and STOP LOSS from MT5 deal reason when available;
- reports exit price and realized MT5 deal profit on CLOSE;
- preserves actual MT5 SL/TP values without inference;
- tracks research order tickets and position IDs so linked lifecycle deals remain observable even when a later deal does not carry the research magic;
- keeps canonical Strategy A disabled.

No Strategy A geometry, entry rule, stop rule, TP rule, order placement logic, or sizing rule was changed.

## Required local action
Restart the Telegram monitor from the updated branch so the new lifecycle logic is loaded.

Existing forward-test process may continue; do not restart it unless needed for another reason.

## Expected Telegram lifecycle
SIGNAL → PENDING ORDER → OPEN/FILL → CLOSE/TAKE PROFIT or CLOSE/STOP LOSS

## Boundary
This is infrastructure/observability only. It does not validate or promote unresolved Strategy A rules and does not enable production trading.
