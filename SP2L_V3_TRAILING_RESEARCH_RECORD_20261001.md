# SP2L V3 Trailing Research Record — 2026-10-01

## Baseline Exit Matrix — completed

Run:
- Version: `SP2L_V3_EXIT_MATRIX_20261001`
- Window: 2026-07-01 00:00 UTC → 2026-10-01 00:00 UTC
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Frozen population: 1,522 signals
- Volume: 0.01
- Contract size: 100
- Spread/slippage/commission: not modeled
- Trailing: completed M1 bar high/low
- Same-bar SL+TP: ambiguous and excluded from decisive metrics
- Status: research-only; trailing is not source-confirmed canonical Strategy A

### Baseline results

| Variant | Decisive | Win rate | Net R | PF | Max DD R | Ambiguous |
|---|---:|---:|---:|---:|---:|---:|
| RR1_NO_TRAIL | 1500 | 61.93% | +358.00 | 1.63 | 11.00 | 22 |
| RR2_NO_TRAIL | 1508 | 43.17% | +445.00 | 1.52 | 16.00 | 14 |
| RR1_TRAIL5 | 1287 | 94.02% | +293.74 | 5.02 | 2.24 | 235 |
| RR1_TRAIL10 | 1259 | 87.13% | +133.36 | 1.88 | 6.18 | 263 |
| RR1_TRAIL15 | 1234 | 80.06% | +30.95 | 1.13 | 14.23 | 288 |
| RR1_TRAIL20 | 1199 | 73.06% | -0.19 | 1.00 | 24.23 | 323 |
| RR1_TRAIL30 | 1293 | 65.74% | +109.28 | 1.25 | 13.49 | 229 |
| RR2_TRAIL5 | 1454 | 94.64% | +475.46 | 7.43 | 2.24 | 68 |
| RR2_TRAIL10 | 1447 | 88.46% | +285.87 | 2.83 | 3.31 | 75 |
| RR2_TRAIL15 | 1439 | 82.14% | +147.56 | 1.59 | 6.34 | 83 |
| RR2_TRAIL20 | 1427 | 75.96% | +83.65 | 1.25 | 14.92 | 95 |
| RR2_TRAIL30 | 1422 | 64.84% | +95.48 | 1.19 | 16.77 | 100 |

### Baseline interpretation

The completed matrix does **not** establish that trailing stop is inherently better or worse. It shows strong sensitivity to trailing distance. Trail 5 and Trail 10 were materially different from Trail 15–30 in this historical replay.

The strongest observed baseline candidate by raw Net R was RR2_TRAIL5 (+475.46R), but this is **not a canonical selection** and must not be promoted from backtest performance alone.

A major audit point is the ambiguous count, especially for RR1 trailing variants. The decisive win rate is conditional on excluding ambiguous outcomes.

## Next experiment: fine-grained Trail sensitivity

The same frozen-population methodology is now extended to:
- Trail 3, 4, 5, 6, 7, 8, 9, 10 pip
- RR1 and RR2
- RR1_NO_TRAIL and RR2_NO_TRAIL retained as baselines

Purpose:
- test whether the apparent Trail5 result is isolated or part of a robust plateau;
- measure Net R, PF, DD, win rate, ambiguity, and losing streak across adjacent trail distances;
- compare July/August/September stability.

This is a sensitivity/robustness experiment only. It does not authorize changing canonical Strategy A rules.

Source status:
- Trailing stop geometry remains unresolved/source-unconfirmed.
- No Trail value is canonical.
