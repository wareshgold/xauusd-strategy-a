# SP2L Four-Week MT5 Stability Results — 2026-09-19

## Status

Research-only evidence. This artifact does not canonicalize unresolved SP2L geometry, promote parameters, authorize live trading, or define production BUY/SELL decisions.

## Frozen research configuration

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Weeks: 2026-08-24 through 2026-09-18 UTC, four complete Monday-Friday weeks
- Harness: existing author-replica MT5 non-overlap stability implementation
- P-Gap: 1.0 research value only
- Spike multiplier: 1.5 research value only
- Max SL: 10 price units research value only
- TP: 1.0R research value only
- Same-bar SL+TP: ambiguous/excluded from decisive WR
- No live trading

## Aggregate result

- Weeks: 4
- Signals: 158
- Decisive: 154
- Wins: 103
- Losses: 51
- Ambiguous: 4
- Open/unresolved: 0
- Decisive WR: 66.883%
- Total R: +52R
- Profit Factor: 2.020

The 95% Wilson interval for the 103/154 decisive win rate is approximately 59.12%–73.83%. This is descriptive uncertainty for this sample and does not establish a production edge.

## Weekly results

| Week UTC | Signals | W | L | A | Decisive WR | Total R | PF | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-09-14 → 2026-09-18 | 38 | 27 | 10 | 1 | 72.973% | +17R | 2.700 | 2R |
| 2026-09-07 → 2026-09-11 | 38 | 26 | 11 | 1 | 70.270% | +15R | 2.364 | 2R |
| 2026-08-31 → 2026-09-04 | 35 | 18 | 16 | 1 | 52.941% | +2R | 1.125 | 4R |
| 2026-08-24 → 2026-08-28 | 47 | 32 | 14 | 1 | 69.565% | +18R | 2.286 | 2R |

## Directional decomposition

The weekly evidence is directionally variable. In 2026-09-07 → 2026-09-11, BUY decisive WR was 46.67% while SELL decisive WR was 86.36%. In the other weeks, BUY and SELL results were materially different again. This indicates that direction-specific stability should remain an explicit robustness question rather than being inferred from the aggregate result.

## Interpretation

1. Expanding from the prior 37 decisive trades to 154 decisive trades preserves positive aggregate Total R (+52R) and PF (2.020).
2. All four weekly slices are positive in Total R, but one week is close to breakeven in R (+2R) and has 52.94% decisive WR.
3. The 95% Wilson interval remains broad enough that the observed 66.88% WR should be treated as an estimate with substantial uncertainty, not as a fixed expected production WR.
4. The four-week result is stronger evidence than the single-week result for reproducibility, but it is still historical in-sample research and is not a fresh post-boundary holdout.
5. The result does not resolve P-Gap, AB=CD, swing/SL, trigger, pending-order lifecycle, or fill semantics.
6. No parameter is promoted and no live-trading authorization follows from this artifact.

## Next gate

Proceed to a four-week robustness/stability analysis using the immutable 4-week dataset and frozen research configuration. Fresh holdout remains separate and must use data after the frozen boundary 2026-09-19 00:00 UTC when eligible data becomes available.
