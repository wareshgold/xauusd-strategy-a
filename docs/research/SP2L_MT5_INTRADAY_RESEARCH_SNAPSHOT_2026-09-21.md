# SP2L MT5 Intraday Research Snapshot — 2026-09-21

## Scope
Research-only intraday replay of the current author-replica candidate on the local MT5 terminal.

This snapshot is **not canonical Strategy A**, does not resolve Strategy A geometry, and does not authorize trading.

## Exact requested interval
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Requested start: 2026-09-21T00:00:00Z
- Requested end: 2026-09-21T11:46:00Z
- Expected minute span: 707
- Raw bars returned: 707
- Bars inside requested interval: 647
- Bars discarded outside interval: 60
- Actual first returned bar in interval: 2026-09-21T01:00:00Z
- Actual last returned bar in interval: 2026-09-21T11:46:00Z
- Unique timestamps: PASS
- Chronological: PASS
- Internal M1 gaps: 0

## Research configuration
- P-Gap price threshold: 1.0
- Spike multiplier: 1.5
- Maximum SL distance: 10.0
- TP: 1R
- Execution: replay only
- Canonical: false

## Results
- Signals detected: 3
- Closed/ambiguous: 3
- Wins: 2
- Losses: 1
- Ambiguous: 0
- Open/unresolved: 0
- Decisive win rate: 66.67%
- Total R: +1R
- Profit factor: 2.00

## Signal ledger
| UTC | Direction | Entry | SL | TP | Outcome |
|---|---|---:|---:|---:|---|
| 03:51 | SELL | 4365.99 | 4370.63 | 4361.35 | LOSS |
| 10:42 | SELL | 4349.23 | 4351.45 | 4347.01 | WIN |
| 11:18 | BUY | 4352.79 | 4349.90 | 4355.68 | WIN |

## Interpretation boundary
The result is a single intraday research observation. It must not be used to select, optimize, or promote unresolved Strategy A rules.

The runner explicitly records:
- timestamp basis is rendered from MT5 epoch as UTC;
- historical MT5 timestamp mapping remains unresolved;
- Strategy A geometry remains unresolved;
- production remains disabled.

## Next gate
The next reproducibility step is API-vs-export equivalence on the same window. No parameter tuning or geometry changes should be made to force agreement.
