# SP2L P-Gap Exact Signal-Set Delta — 2026-09-22

## Status

Research-only. This result does **not** promote any P-Gap threshold to canonical geometry.

Source authority remains controlling: P-Gap semantics are source-confirmed, but executable boundaries/indexing and exact threshold remain unresolved.

## Dataset

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Window: 2026-09-14 00:00 UTC through 2026-09-18 23:59:59 UTC
- Returned bars: 10,000
- Candidate runner: `run-author-replica-mt5-nonoverlap-stability.py`
- P-Gap values: 0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2 price units

## Exact set counts

| P-Gap | Signals | Removed vs P-Gap 0 |
|---:|---:|---:|
| 0.00 | 56 | 0 |
| 0.25 | 54 | 2 |
| 0.50 | 46 | 10 |
| 0.75 | 42 | 14 |
| 1.00 | 38 | 18 |
| 1.25 | 24 | 32 |
| 1.50 | 19 | 37 |
| 2.00 | 12 | 44 |

All comparisons use exact timestamp + direction membership.

## Key finding

The signal sets are strictly nested as P-Gap increases.

There were **zero additions** at every threshold transition. Every increase in P-Gap only removed previously admitted setups.

Adjacent removals:

- 0 → 0.25: 2
- 0.25 → 0.5: 8
- 0.5 → 0.75: 4
- 0.75 → 1.0: 4
- 1.0 → 1.25: 14
- 1.25 → 1.5: 5
- 1.5 → 2.0: 7

The largest local selection change is 1.0 → 1.25, removing 14 of the 38 P-Gap=1 setups (36.8%).

## Interpretation

This establishes a deterministic selection effect for the current research predicate:

- P-Gap is not performance-neutral; it materially changes the candidate signal population.
- Increasing the threshold acts as a one-way filter on the existing candidate set.
- The sharpest reduction in this sample occurs above 1.0 price units.
- This does **not** identify the teacher's threshold or prove that 1.0 is correct.
- It also does not establish that the current three-candle P-Gap predicate itself is the teacher's executable geometry.

The result therefore supports further **geometry/selection diagnostics**, not canonical promotion.

## Next research discriminator

The next useful test is to measure the actual source-candidate gap magnitude for every admitted setup and classify the removed setups by gap interval. This can show whether the observed 1.0→1.25 drop is a natural concentration boundary in the research data or merely an artifact of the chosen heuristic.

That analysis must remain descriptive and cannot select a canonical threshold.

## Gate state

- P-Gap semantics: SOURCE-CONFIRMED
- P-Gap executable geometry: UNRESOLVED
- Frozen Geometry: BLOCKED
- Production: OFF
