# RR2/TRAIL4 Telegram Forward-Test Checkpoint — 2026-10-13

## Purpose
Checkpoint Telegram notification evidence before the next historical trailing-management backtest. This is a research/demo operational snapshot, not a strategy-performance certification.

## Repository state
- Telegram lifecycle fix PR: #289, merged.
- Merge commit: `4307381e97fdbbc3b5cd61751f43a377a3038ab7`.
- Focused deterministic GitHub Actions workflow for that merge: completed successfully.
- Separate market-data diagnostic PR #293 remains open and is not part of this checkpoint; no evidence in this checkpoint establishes that missing market data was the cause of the earlier quiet event period.

## Evidence observed in the user's local event log
- Runner START at `2026-10-13T08:50:44Z`; startup Telegram event returned `success=true`, `HTTP_200`.
- Candidate signal at `2026-10-13T08:57:09Z`; order request was accepted and verified against the active order.
- `TELEGRAM_SIGNAL` at `2026-10-13T08:57:10Z` returned `success=true`, `HTTP_200`.
- The user-provided recent lifecycle sample contains multiple `TELEGRAM_DEAL_LIFECYCLE` events with nested `telegram.success=true` and `HTTP_200`, including both zero-profit entry records and closed-deal records with net results.
- The user reported a newly closed trade with +$0.23. The supplied excerpt did not include the matching close event for that specific trade, so that exact trade is not yet independently reconciled to its event ticket/deal.
- These records establish successful Telegram API acknowledgements for the listed events, not that a human viewed the messages. Telegram sendMessage does not provide exactly-once delivery guarantees.

## Scope / safety
- `canonical=false`; demo/research only.
- No geometry, entry/exit rules, order sizing, trailing configuration, or active runner state was changed as part of this checkpoint.
- Do not alter the current Trail4 distance while planning the historical backtest.
- Preserve the existing JSONL and state files. No cleanup or restart is implied by this snapshot.

## Next sequence
1. Reconcile the reported +$0.23 close against its matching `TELEGRAM_DEAL_LIFECYCLE` record; if necessary inspect only the latest matching events.
2. Prepare a deterministic historical comparison of trailing-management variants using the same dataset, signal set, and exit-resolution rules. The first matrix is gross (spread, commission, swap, and slippage excluded) and isolates one primary entry; record this limitation and add costs/2X only in a separate follow-up. Do not choose settings from a single favorable metric; report R, drawdown, profit factor, win rate, trade count, ambiguity count, and stability by time segment.
3. Freeze the tested parameter grid and record all assumptions before comparing results. Treat any unresolved source geometry as unresolved; the backtest cannot make a source rule canonical.
4. Only after the user selects a tested research configuration, update the forward-test configuration in a controlled, documented change and take a fresh runtime snapshot.
5. Return to Factory work after the backtest/configuration decision.

## Explicitly unresolved
- The exact +$0.23 deal-to-event reconciliation.
- Whether the current local process is running precisely the merged PR #289 code; event behavior is consistent with successful notifications, but the process revision cannot be proven from JSONL alone.
- The best trailing-management parameters; these must be measured in the requested backtest, not inferred from forward samples.
