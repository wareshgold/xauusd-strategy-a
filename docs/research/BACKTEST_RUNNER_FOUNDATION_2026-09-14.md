# Backtest Runner Foundation — 2026-09-14

## Purpose

Connect the deterministic replay engine, execution simulator, trade ledger, and descriptive metrics into one reproducible research runner.

## Pipeline

OHLC candles → deterministic decisions → pending execution events → realized trade outcomes → descriptive R metrics.

## Determinism boundaries

- Trade IDs are generated from a deterministic sequence.
- Candles are processed in supplied chronological order.
- Metrics preserve realized trade order for drawdown and loss-streak calculations.
- Simultaneous stop/target touches remain `AMBIGUOUS`; no intrabar ordering is invented.
- Execution semantics remain the explicitly supplied simulator policy and are not claimed to be canonical Strategy A semantics.

## Strategy boundary

The runner does not create or infer P-Gap geometry, A/B/C/D anchors, fill semantics, structural invalidation, target mapping, session filters, or other unresolved Strategy A rules.

A successful run of this runner is therefore **infrastructure validation**, not evidence of Strategy A profitability or source validation.

## Next

Add a versioned dataset/run manifest and a report serializer so every research run records its exact data identity, strategy specification, execution-policy identity, counts, unresolved events, and metrics.
