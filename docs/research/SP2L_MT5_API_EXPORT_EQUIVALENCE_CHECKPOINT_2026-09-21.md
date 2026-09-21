# SP2L MT5 API-vs-Export Equivalence Checkpoint — 2026-09-21

## Scope

Research-only reproducibility checkpoint for the author-replica candidate on the exact same MT5 window.

This checkpoint does **not** make Strategy A canonical, does **not** resolve P-Gap or other geometry, and does **not** authorize trading.

## Exact window

- Symbol: XAUUSD.ecn
- Server: OtetGroup-MT5
- Timeframe: M1
- Requested start: 2026-09-21T00:00:00Z
- Requested end: 2026-09-21T11:46:00Z
- Expected minute span: 707

## API acquisition

Local execution of `scripts/run-author-replica-mt5-api.py` returned:

- Raw bars: 707
- Bars inside interval: 647
- Bars discarded outside interval: 60
- First in interval: 2026-09-21T01:00:00Z
- Last in interval: 2026-09-21T11:46:00Z
- Unique timestamps: PASS
- Chronological: PASS
- Internal M1 gaps: 0

Configuration:

- P-Gap price threshold: 1.0
- Spike multiplier: 1.5
- Maximum SL distance: 10.0
- TP: 1R

## Export snapshot comparison

The committed research snapshot at commit `7fd80a9` reports the same:

- Raw bars: 707
- Bars inside interval: 647
- Bars discarded outside interval: 60
- First in interval: 2026-09-21T01:00:00Z
- Last in interval: 2026-09-21T11:46:00Z
- Unique timestamps: PASS
- Chronological: PASS
- Internal M1 gaps: 0

## Signal/outcome equivalence

API result:

| UTC | Direction | Entry | SL | TP | Outcome |
|---|---|---:|---:|---:|---|
| 03:51 | SELL | 4365.99 | 4370.63 | 4361.35 | LOSS |
| 10:42 | SELL | 4349.23 | 4351.45 | 4347.01 | WIN |
| 11:18 | BUY | 4352.79 | 4349.90 | 4355.68 | WIN |

Aggregate:

- Signals: 3
- Closed/ambiguous: 3
- Wins: 2
- Losses: 1
- Ambiguous: 0
- Open/unresolved: 0
- Decisive win rate: 66.67%
- Total R: +1R
- Profit factor: 2.00

These match the committed export snapshot exactly at the reported comparison fields and signal ledger.

## Gate result

**API-vs-Export Equivalence: PASS for this exact window.**

This is a reproducibility observation for one window, not a historical-data equivalence proof for all MT5 periods.

## Remaining blockers

- Historical MT5 timestamp basis: UNRESOLVED
- Strategy A Frozen Geometry: BLOCKED
- Canonical P-Gap executable geometry: UNRESOLVED
- Production: DISABLED

## Next gate

Run additional independent same-window API-vs-export comparisons. No parameter tuning, timestamp shifting, or geometry changes may be introduced to force agreement.
