# SP2L V2 — Provenance of 2026-09-27 05:22Z Result

Status: RESEARCH FORENSICS — NOT CANONICAL

## Identified run

The run that produced the reported result:

- Report: `artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260927T052251Z.json`
- Execution time: approximately 2026-09-27 05:22:51Z
- Window: 2026-09-14T00:00:00Z through 2026-09-25T23:59:59Z
- Requested symbol: XAUUSD
- Resolved symbol: XAUUSD.ecn
- Timeframe: M1
- MT5 terminal: Otet Group MT5
- Runner commit: `a836ed038ae84a401b32dfc27690ddb04044de01`
- Runner change: `fix V2 MT5 broker symbol resolution`
- Detector at that commit: `scripts/sp2l_strategy_a_v2_detector.py`
- Detector SHA256/blob SHA: `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`

## Reported result

The result recorded during today's execution was:

- Signals: 222
- Decisive: 204
- Wins: 127
- Losses: 77
- Decisive win rate: 62.2549019608%
- Net: +50R
- Profit factor: 1.64935064935
- Max drawdown: 6R
- Max consecutive losses: 5

## Configuration reported for the run

- P-Gap: 1.0
- Spike multiplier: 1.5
- Max SL: 10.0
- TP: 1R
- 2X: OFF
- Trailing: OFF
- Breakeven: OFF
- EMA/ATR/ADX/trend filters: OFF
- Session filter: OFF (reported configuration; artifact provenance still needs direct inspection)
- SL anchor: candle before Spike Low/High

## What is proven

1. The exact Git commit that was immediately used before the reported 05:22Z execution is identified: `a836ed0`.
2. That commit contains the V2 MT5 runner and the same V2 detector contract used in the subsequent research work.
3. The detector content at `a836ed0` has the same blob SHA as the current V2 detector: `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`.
4. Therefore the discrepancy is not explained by a detector revision between `a836ed0` and the current V2 detector.

## What is not yet proven

The JSON report itself is not present in the GitHub repository history, so the following cannot yet be independently hashed from the repository:

- the exact 222-signal ledger;
- the exact 204-decisive subset;
- the exact MT5 raw-bar acquisition output used by that run;
- the exact report-side outcome/ambiguity fields;
- whether any local uncommitted runner changes existed at execution time.

The current controlled source-baseline run on the same requested window produced 227 signals / 220 decisive / 124 wins / 96 losses / 5 ambiguous / 2 no-fill / +28R. This is a separate result and must not be selected over the 222 result without ledger reconciliation.

## Next forensic step

Reproduce the `a836ed0` runner contract against the current connected MT5 terminal and emit a complete immutable signal ledger. Then compare it against the current dedicated V2 baseline ledger using multiplicity-preserving matching.

The existing reconciliation tool at `d971af7` uses dictionary fingerprints and therefore must be hardened to detect duplicate fingerprints before it is used for the final parity verdict.

No result is canonical.