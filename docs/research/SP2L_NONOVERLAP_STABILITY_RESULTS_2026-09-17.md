# SP2L Author Replica — Non-Overlap Stability Results

**Date:** 2026-09-17  
**Purpose:** research-only stability diagnostic for the author-associated SP2L implementation candidate.  
**Canonical status:** NOT canonical Strategy A; Frozen Geometry remains blocked.

## Fixed configuration

- Source: `MetaTrader5.copy_rates_from`
- Terminal: Otet Group MT5 Terminal
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Requested bars per snapshot: 10,000
- P-Gap price: 1.0
- Spike multiplier: 1.5
- Max SL price: 10.0
- TP: 1R
- Requested snapshot-end spacing: 12 days

## Snapshot results

| Snapshot end UTC | First UTC | Last UTC | Signals | Wins | Losses | Ambiguous | Decisive WR | Total R | PF |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-09-17 10:45 | 2026-09-08 05:00 | 2026-09-17 10:45 | 62 | 44 | 16 | 2 | 73.33% | +28 | 2.75 |
| 2026-09-05 10:45 | 2026-08-26 18:11 | 2026-09-04 23:58 | 54 | 29 | 24 | 1 | 54.72% | +5 | 1.21 |
| 2026-08-24 10:45 | 2026-08-13 04:59 | 2026-08-24 10:45 | 55 | 34 | 20 | 1 | 62.96% | +14 | 1.70 |
| 2026-08-12 10:45 | 2026-08-03 04:58 | 2026-08-12 10:45 | 45 | 30 | 15 | 0 | 66.67% | +15 | 2.00 |
| 2026-07-31 10:45 | 2026-07-22 04:58 | 2026-07-31 10:45 | 46 | 31 | 15 | 0 | 67.39% | +16 | 2.07 |
| 2026-07-19 10:45 | 2026-07-08 18:14 | 2026-07-17 23:57 | 39 | 22 | 17 | 0 | 56.41% | +5 | 1.29 |

## Descriptive aggregate

Across the six snapshots, there are 190 wins, 117 losses, and 5 ambiguous outcomes. The pooled decisive result is 190 / 307 = **61.89%**. Pooled decisive R is **+73R** and pooled decisive profit factor is approximately **1.62**.

This pooled aggregation is descriptive only. The six windows are non-overlapping in their returned calendar coverage, but trades within and across windows are not assumed independent, and execution/fill semantics remain unresolved.

## Findings

1. The 73.33% observation is **not isolated**: four of six snapshots are above 60%.
2. The result is also **not uniformly above 60%**: two snapshots are below 60% (54.72% and 56.41%).
3. Every snapshot has positive total R under this research implementation and accounting, ranging from +5R to +28R.
4. The current evidence therefore supports a statement of **repeatability across several separated historical windows**, not a claim of a stable canonical edge.
5. A 60% threshold is not adopted as a pass/fail gate merely because the observed results cluster around it. Any formal stability criterion must be specified independently of these outcomes.
6. No P-Gap, spike, entry, SL, fill, AB=CD, Round Level, or lifecycle rule is changed as a consequence of these results.

## Next research gate

The next step should increase temporal coverage and preserve the fixed implementation/configuration. Before any untouched validation or production consideration, continue source resolution—especially F14 AB=CD and unresolved execution/fill semantics—and then define a pre-registered stability/validation protocol.
