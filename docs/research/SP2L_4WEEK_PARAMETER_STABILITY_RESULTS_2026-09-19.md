# SP2L 4-Week Parameter Stability Results — 2026-09-19

## Status

Research-only robustness evidence. No parameter is promoted and no production/live authorization follows from this report.

## Dataset and frozen surface

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Historical partitions: 2026-08-24 → 2026-09-18 UTC, four complete Monday-Friday weeks
- Parameter combinations: 81
- P-Gap grid: 0.8 / 1.0 / 1.2
- Spike multiplier grid: 1.3 / 1.5 / 1.7
- Max SL grid: 8 / 10 / 12
- TP grid: 0.8R / 1.0R / 1.2R
- Baseline: 1.0 / 1.5 / 10 / 1.0R

## S1 — Surface concentration

Across all 81 combinations:

- Decisive WR minimum: 59.794%
- Q1: 63.131%
- Median: 65.972%
- Q3: 68.639%
- Maximum: 70.968%
- Total R minimum: +25R
- Q1: +38R
- Median: +46R
- Q3: +52R
- Maximum: +70R
- Positive Total R: 81/81 (100%)
- Above 60% decisive WR: 80/81 (98.77%)

Interpretation: the positive result is distributed across the tested parameter surface rather than concentrated in one narrow combination. One combination is below the 60% descriptive reference, but it remains positive in Total R.

## S2 — Baseline locality

Baseline: 66.883% decisive WR, +52R, PF 2.020.

### P-Gap

- 0.8: WR -2.002 percentage points; Total R -2R; PF -0.172
- 1.2: WR -0.741 percentage points; Total R -11R; PF -0.066

Both neighboring values remain positive. The 1.2 setting reduces Total R more materially but does not create a failure boundary.

### Spike multiplier

- 1.3: WR -1.137 percentage points; Total R +5R; PF -0.100
- 1.7: WR -0.216 percentage points; Total R -10R; PF -0.020

Both neighbors remain positive. WR changes are small and there is no isolated collapse around the baseline.

### Max SL

- 8: WR -0.216 percentage points; Total R -2R; PF -0.020
- 12: WR unchanged; Total R unchanged; PF unchanged

The tested max-SL neighbors do not show a discontinuity.

### TP

- 0.8R: WR +4.085 percentage points; Total R +13R; PF +0.425
- 1.2R: WR -3.012 percentage points; Total R -9R; PF -0.252

TP shows the largest local sensitivity in this matrix. The response remains continuous and both neighboring settings remain positive, but TP is the parameter with the clearest measured effect in the tested surface.

The 0.8R result is a sensitivity observation only; it is not a recommendation or canonical promotion.

## S3 — Temporal consistency

The four-week baseline decisive WR values are:

- 72.973%
- 70.270%
- 52.941%
- 69.565%

Minimum: 52.941%  
Maximum: 72.973%  
Weeks above 60%: 3/4

This remains mixed temporal evidence. Therefore parameter-surface robustness is positive, while temporal stability remains **INCONCLUSIVE**.

## S4 — Main-effect interpretation

The available matrix summary supports descriptive sensitivity analysis, but the aggregate output alone does not provide the full per-level distributions needed for a complete S4 table. No causal or optimization conclusion is drawn from the aggregate.

## S5 — Multiple-testing guard

The 81-combination surface is explicitly treated as a multiple-comparison research surface. The best-performing combination is not selected as a production configuration.

## S6 — Statistical uncertainty

The baseline is 103 wins / 51 losses among 154 decisive observations. The previously established descriptive Wilson 95% interval is approximately 59.12%–73.83%. This does not represent an out-of-sample guarantee or independent-trial assumption.

## Gate disposition

**Parameter Stability Gate: POSITIVE EVIDENCE**

Reason:

1. 81/81 tested combinations have positive Total R.
2. 80/81 remain above the 60% descriptive WR reference.
3. Baseline neighbors do not show an isolated performance cliff.
4. TP has measurable sensitivity, but the response across tested values remains positive rather than collapsing.
5. Multiple-testing is explicitly guarded against.

This disposition applies only to the declared parameter-stability surface. It does not resolve source geometry and does not override the separate temporal-stability, Frozen Geometry, or Fresh Holdout gates.

## Production status

Production/live trading remains **BLOCKED**.

Frozen Geometry remains **BLOCKED**.

Temporal/Rolling Stability remains **INCONCLUSIVE — NO PASS / NO FAIL**.

Fresh Holdout remains **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**.

Live trading remains **DISABLED**.
