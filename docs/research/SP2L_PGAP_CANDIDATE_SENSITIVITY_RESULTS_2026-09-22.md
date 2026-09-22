# SP2L Research Candidate V0.1 — P-Gap Sensitivity Results — 2026-09-22

## Scope

Research-only MT5 M1 stability sweep on XAUUSD.ecn using six non-overlapping snapshot endpoints and the existing author-replica runner.

Fixed:
- Spike multiplier: 1.5
- Max SL distance: 10.0
- TP R: 1.0
- Requested bars per snapshot: 10,000
- P-Gap candidates: 0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2.0

This experiment does not define canonical Strategy A geometry.

## Aggregate results

| P-Gap | Signals | Wins | Losses | Ambiguous | Decisive WR | Total R | Aggregate PF |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 494 | 312 | 172 | 10 | 64.46% | +140R | 1.81 |
| 0.25 | 456 | 285 | 163 | 8 | 63.62% | +122R | 1.75 |
| 0.50 | 404 | 247 | 152 | 5 | 61.90% | +95R | 1.63 |
| 0.75 | 355 | 217 | 132 | 5 | 62.18% | +85R | 1.64 |
| 1.00 | 301 | 190 | 107 | 4 | 63.97% | +83R | 1.78 |
| 1.25 | 245 | 152 | 92 | 1 | 62.30% | +60R | 1.65 |
| 1.50 | 199 | 126 | 72 | 1 | 63.64% | +54R | 1.75 |
| 2.00 | 131 | 85 | 46 | 0 | 64.89% | +39R | 1.85 |

## Observations

1. Increasing P-Gap monotonically reduces signal count in this six-window sample.
2. Decisive win rate remains in a relatively narrow band (~61.9%–64.9%); there is no isolated performance spike at P-Gap=1.0.
3. P-Gap=1.0 is therefore **not statistically or source-wise selected by this sweep**.
4. P-Gap=0 produces the largest aggregate R because it admits substantially more signals; this must not be interpreted as evidence that zero-gap is the source rule.
5. P-Gap=2.0 has the highest aggregate decisive WR among these candidates, but on only 131 signals and with much lower total R; this also does not establish a canonical threshold.
6. The experiment demonstrates that P-Gap is materially affecting the signal set, while not identifying the teacher's exact executable geometry.
7. Source resolution remains the controlling gate.

## Six-snapshot stability note

The weekly/snapshot results remain heterogeneous. In particular, P-Gap=1.0 ranges from 54.72% to 73.33% decisive WR across the six snapshots. This confirms that the candidate should not be promoted or traded based on aggregate performance alone.

## Decision

**No P-Gap value is promoted to canonical.**

The current source status remains:
- P-Gap semantic: SOURCE-CONFIRMED
- P-Gap executable geometry: UNRESOLVED
- Frozen Geometry: BLOCKED
- Production: OFF

Next research action: preserve the candidate sweep and compare exact signal-set deltas/condition diagnostics; seek genuinely new primary visual evidence for the disputed P-Gap boundaries rather than optimizing the numeric threshold from backtest results.
