# SP2L Parameter Robustness Analysis — 2026-09-19

## Status

- Research stage: Robustness / Parameter Sensitivity
- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`
- Input artifact: `artifacts/SP2L_author_replica_parameter_robustness_matrix.json`
- Matrix size: 81 combinations
- Canonical strategy geometry: unchanged
- Canonical parameters: unchanged
- Fresh holdout: NOT RUN
- Production/live trading decision: NOT AUTHORIZED by this analysis

## Purpose

This analysis evaluates sensitivity of the existing Author-Replica implementation to the four parameter dimensions already exposed by the robustness runner. It does not define or promote new canonical rules.

Tested grid:

- P-Gap: 0.8 / 1.0 / 1.2
- Spike Multiplier: 1.3 / 1.5 / 1.7
- Max SL: 8 / 10 / 12
- TP: 0.8R / 1.0R / 1.2R

The source-first rule remains in force: backtest performance cannot resolve source ambiguity and cannot promote a parameter to canonical status.

## Baseline

Baseline parameters:

- P-Gap = 1.0
- Spike Multiplier = 1.5
- Max SL = 10
- TP = 1.0R

Baseline result:

- Signals: 158
- Wins: 103
- Losses: 51
- Ambiguous: 4
- Decisive observations: 154
- Decisive win rate: 66.883%
- Total R: +52R
- Profit factor: 2.020
- Minimum weekly decisive WR: 52.941%
- Maximum weekly decisive WR: 72.973%
- Weeks above 60% WR: 3/4
- Weekly decisive WR: 72.973%, 70.270%, 52.941%, 69.565%

Approximate 95% Wilson interval for the baseline decisive win rate, treating the 154 decisive outcomes as a binomial sample for descriptive uncertainty only: 59.1%–73.8%. This is not a claim that trades are independent or identically distributed.

## Full Matrix Distribution

Across all 81 combinations:

| Metric | Result |
|---|---:|
| Mean decisive WR | 65.733% |
| Median decisive WR | 65.972% |
| Minimum decisive WR | 59.794% |
| Maximum decisive WR | 70.968% |
| Mean Total R | +46.19R |
| Median Total R | +46R |
| Minimum Total R | +25R |
| Maximum Total R | +70R |
| Mean PF | 1.939 |
| Median PF | 1.939 |
| Minimum PF | 1.487 |
| Maximum PF | 2.444 |
| Positive Total R combinations | 81/81 |
| Combinations above 60% WR | 80/81 |

The baseline WR is 0.91 percentage points above the matrix median, so the baseline is not an isolated WR maximum.

## Direct One-Parameter Neighbors

Holding the other three baseline parameters fixed:

| Changed parameter | Value | WR | Total R | PF | Min weekly WR |
|---|---:|---:|---:|---:|---:|
| P-Gap | 0.8 | 64.881% | +50R | 1.847 | 55.263% |
| P-Gap | 1.2 | 66.142% | +41R | 1.953 | 51.852% |
| Spike Multiplier | 1.3 | 65.746% | +57R | 1.919 | 55.000% |
| Spike Multiplier | 1.7 | 66.667% | +42R | 2.000 | 53.571% |
| Max SL | 8 | 66.667% | +50R | 2.000 | 52.941% |
| Max SL | 12 | 66.883% | +52R | 2.020 | 52.941% |
| TP | 0.8R | 70.968% | +65R | 2.444 | 60.000% |
| TP | 1.2R | 63.871% | +43R | 1.768 | 52.941% |

No direct one-parameter neighbor shows a performance collapse.

## Locality / Plateau Interpretation

Because each parameter has exactly three tested levels, the complete 3x3x3x3 grid contains all combinations in the declared test range. Therefore, "neighborhood" here means robustness within the tested range; it does not establish behavior outside the tested bounds.

All 81 combinations are inside that tested range. The WR range is relatively compressed (59.794%–70.968%), while Total R varies more materially (+25R to +70R). This indicates that parameter changes affect payoff distribution more than they affect the basic win-rate regime.

The highest WR occurs at TP=0.8R with baseline P-Gap/Spike/SL settings (70.968%, +65R, PF 2.444). This is a performance observation only. It is not a canonical-parameter recommendation, because source evidence does not authorize selecting a canonical TP by optimizing this matrix.

The baseline ranks approximately 26th of 81 by decisive WR. Its non-maximal rank is consistent with a broad performance region rather than optimization around a single WR peak.

## Weekly Stability

The baseline has one weaker week:

- 72.973%
- 70.270%
- 52.941%
- 69.565%

Thus 3/4 weeks exceed 60%, but the minimum week is 52.941%. This prevents the aggregate 66.883% result from being interpreted as uniformly stable across the four observed weeks.

Only 6 of the 81 combinations have all four observed weeks above 60% decisive WR. This statistic is descriptive and should not be converted into an unplanned acceptance threshold.

## Interpretation

### Positive evidence

1. The 81-point parameter surface is not dominated by a single high-WR point.
2. Baseline WR is close to the matrix median.
3. All tested combinations have positive Total R in this sample.
4. 80/81 combinations exceed 60% decisive WR.
5. Direct one-parameter perturbations do not produce a collapse.
6. The baseline's approximate confidence interval is materially wider than the difference between baseline and matrix median, so the small baseline-vs-median WR difference should not be overinterpreted.

### Remaining limitations

1. The matrix uses the same historical sample as the development/backtest context; it is not an untouched validation set.
2. The 81 combinations were evaluated within a bounded parameter grid only.
3. The observed weekly minimum remains materially below the aggregate WR.
4. Parameter selection based on this matrix would introduce research-selection bias if used to choose a production setting before fresh validation.
5. Source ambiguity remains authoritative wherever geometry or execution semantics are not source-confirmed.
6. This matrix does not establish live execution quality, slippage, spread effects, broker-specific fills, or timestamp/calendar completeness beyond the data assumptions already documented elsewhere.

## Gate Disposition

**ROBUSTNESS EVIDENCE: POSITIVE**

The parameter surface provides evidence against a single isolated performance peak within the tested range.

**PARAMETER STABILITY GATE: PENDING**

The matrix alone is not sufficient to authorize the next production step. The next required stage is an untouched Fresh Holdout using frozen rules/parameters, with no parameter tuning based on the holdout.

**FRESH HOLDOUT: NOT STARTED**

**PRODUCTION: BLOCKED**

## Canonical-Rules Guard

This analysis does NOT:

- change P-Gap geometry;
- define AB=CD anchors or tolerance;
- define fill semantics;
- make Leg1=Leg2 equality canonical;
- select TP=0.8R as a canonical rule;
- select any parameter combination because it has the highest backtest result;
- authorize BUY/SELL production decisions.

The artifact is a robustness/sensitivity record only.
