# SP2L Parameter Stability Assessment — 2026-09-19

## Scope

This assessment applies the pre-registered protocol in `docs/research/SP2L_PARAMETER_STABILITY_PROTOCOL_2026-09-19.md` to the already archived 81-combination robustness results. It does not alter source geometry, frozen parameters, or the Fresh Holdout boundary.

## S1 — Surface concentration

Archived matrix:

- 81/81 combinations had positive Total R.
- 80/81 combinations had decisive WR above 60%.
- Mean decisive WR: 65.733%.
- Median decisive WR: 65.972%.
- Minimum decisive WR: 59.794%.
- Maximum decisive WR: 70.968%.
- Mean Total R: +46.19R.
- Median Total R: +46R.
- Minimum Total R: +25R.
- Maximum Total R: +70R.
- Mean PF: 1.939.
- Median PF: 1.939.
- Minimum PF: 1.487.
- Maximum PF: 2.444.

The observed WR surface is comparatively compressed relative to the Total-R range. The baseline WR (66.883%) is only 0.911 percentage points above the matrix median and is not the maximum.

**S1 disposition: POSITIVE STABILITY EVIDENCE within the tested grid.**

This does not establish behavior outside the tested parameter bounds.

## S2 — Baseline locality

One-parameter neighbors around the baseline:

| Parameter | Lower level WR | Baseline WR | Upper level WR | Interpretation |
|---|---:|---:|---:|---|
| P-Gap | 64.881% | 66.883% | 66.142% | no collapse |
| Spike Multiplier | 65.746% | 66.883% | 66.667% | no collapse |
| Max SL | 66.667% | 66.883% | 66.883% | no collapse |
| TP | 70.968% | 66.883% | 63.871% | larger sensitivity, still no collapse |

The corresponding Total-R values also remain positive for every direct neighbor. TP shows the largest local sensitivity, but this is a descriptive stability observation and is not a parameter-selection rule.

**S2 disposition: POSITIVE, with TP identified as the more sensitive tested dimension.**

## S3 — Temporal consistency

Baseline weekly decisive WR:

- 72.973%
- 70.270%
- 52.941%
- 69.565%

Derived descriptive statistics:

- Minimum: 52.941%
- Maximum: 72.973%
- Mean: approximately 66.437%
- Population standard deviation: approximately 8.20 percentage points
- Weeks above 60%: 3/4

The 52.941% week is a meaningful deviation from the aggregate result. Therefore the aggregate WR should not be described as uniformly stable across time.

**S3 disposition: MIXED / INCONCLUSIVE.**

## S4 — Parameter main effects

The archived analysis contains direct-neighbor observations but does not expose a complete level-by-level aggregate table in the current assessment input. A full main-effect calculation must use the original 81-row matrix artifact directly.

No main-effect result is invented here.

**S4 disposition: PENDING RAW-MATRIX COMPUTATION.**

## S5 — Multiple-testing guard

The 81-combination search surface is explicitly treated as a research sensitivity surface. The highest-performing combination is not promoted to canonical status.

No parameter optimization or re-selection is performed by this assessment.

**S5 disposition: PASS.**

## S6 — Statistical uncertainty

For the baseline, 103 wins among 154 decisive observations gives an approximate 95% Wilson interval of 59.1%–73.8%.

This interval is descriptive only. It does not account for serial dependence, regime dependence, repeated use of the same historical sample, execution uncertainty, or multiple testing.

The interval is substantially wider than the 0.911 percentage-point difference between baseline WR and matrix median; that small difference should therefore not be overinterpreted.

**S6 disposition: DESCRIPTIVE / LIMITED.**

## Stability Gate

Current evidence supports:

- no isolated single-point WR peak dominating the tested surface;
- no collapse in direct one-parameter baseline neighbors;
- positive Total R throughout the tested 81-point surface;
- explicit protection against selecting a best parameter from the matrix.

However:

- temporal stability is mixed because one of four observed weeks is materially weaker;
- complete main-effect aggregation still requires direct use of the archived raw matrix.

### Current gate status

**PARAMETER STABILITY: INCONCLUSIVE / PENDING COMPLETION**

This is not a failure of the strategy. It means the pre-registered assessment cannot honestly be marked fully passed until S4 is computed from the raw 81-row artifact.


## S4 — Complete Parameter Main Effects

The archived raw 81-row matrix was retrieved directly and aggregated by each parameter level. Each level represents 27 combinations; aggregation uses the sum of wins divided by the sum of decisive wins+losses across those combinations.

| Parameter | Level | Decisive WR | Mean Total R | Mean PF | Mean min-week WR |
|---|---:|---:|---:|---:|---:|
| P-Gap | 0.8 | 64.415% | +47.89R | 1.842 | 56.06% |
| P-Gap | 1.0 | 66.546% | +50.67R | 2.015 | 55.85% |
| P-Gap | 1.2 | 66.071% | +40.00R | 1.960 | 53.67% |
| Spike Multiplier | 1.3 | 64.971% | +52.33R | 1.884 | 55.97% |
| Spike Multiplier | 1.5 | 66.019% | +47.67R | 1.969 | 54.95% |
| Spike Multiplier | 1.7 | 66.050% | +38.56R | 1.964 | 54.66% |
| Max SL | 8 | 65.495% | +45.07R | 1.932 | 55.20% |
| Max SL | 10 | 65.673% | +46.74R | 1.943 | 55.20% |
| Max SL | 12 | 65.673% | +46.74R | 1.943 | 55.20% |
| TP | 0.8R | 68.867% | +55.89R | 2.227 | 58.40% |
| TP | 1.0R | 65.561% | +45.89R | 1.920 | 53.86% |
| TP | 1.2R | 62.416% | +36.78R | 1.670 | 53.33% |

### S4 interpretation

The main-effect surface shows that TP has the largest tested effect on aggregate decisive WR and payoff. P-Gap and Spike Multiplier show smaller shifts, while Max SL is nearly flat between the tested levels 10 and 12. These are descriptive sensitivity results only; they do not authorize parameter re-selection.

**S4 disposition: COMPLETE / DESCRIPTIVE.**

## Final Stability Gate Disposition

All six protocol sections are now recorded. The evidence does not support calling the temporal behavior uniformly stable: the baseline has one materially weaker observed week (52.941%), and the main-effect surface confirms that TP sensitivity is non-trivial.

Therefore:

**PARAMETER STABILITY GATE: INCONCLUSIVE — NO PASS / NO FAIL**

This is a deliberate evidence-status result, not a production rejection. The current historical matrix supports robustness within the tested grid, but the temporal sample is too limited to declare stability sufficient for production.

The untouched Fresh Holdout remains the required independent evidence gate. It must use the frozen configuration and frozen boundary, with no tuning from holdout observations.

**PRODUCTION: BLOCKED.**
