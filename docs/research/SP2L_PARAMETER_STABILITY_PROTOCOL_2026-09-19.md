# SP2L Parameter Stability Protocol — 2026-09-19

## Status

- Stage: Robustness / Parameter Stability
- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`
- Input: previously completed 81-combination Author-Replica robustness matrix
- Purpose: pre-register an objective stability assessment before Fresh Holdout
- Canonical strategy geometry: unchanged
- Canonical parameters: unchanged
- Fresh Holdout: not yet eligible because no post-boundary bars were available on 2026-09-19
- Production: blocked

## Source-first boundary

This protocol evaluates the behavior of an existing research implementation. It does not define Strategy A geometry and cannot resolve:

- P-Gap source geometry;
- AB=CD anchors or tolerance;
- fill semantics;
- Leg 1 / Leg 2 equality;
- pending-order lifecycle;
- any other unresolved source rule.

A parameter value is not canonical merely because it performs better in this research matrix.

## Existing matrix

The completed matrix contains all 81 combinations of:

- P-Gap: 0.8 / 1.0 / 1.2
- Spike Multiplier: 1.3 / 1.5 / 1.7
- Max SL: 8 / 10 / 12
- TP: 0.8R / 1.0R / 1.2R

Baseline:

- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R

Existing descriptive evidence:

- Baseline decisive WR: 66.883%
- Baseline Total R: +52R
- Baseline PF: 2.020
- Matrix mean decisive WR: 65.733%
- Matrix median decisive WR: 65.972%
- Matrix WR range: 59.794%–70.968%
- Matrix Total R range: +25R to +70R
- 81/81 combinations positive Total R
- 80/81 combinations above 60% decisive WR
- Baseline weekly decisive WR: 72.973%, 70.270%, 52.941%, 69.565%

These are descriptive development-sample observations, not holdout evidence.

## Pre-registered stability checks

The following checks are applied to the already declared parameter surface without selecting a new production parameter.

### S1 — Surface concentration

Measure whether performance is concentrated in a narrow part of the tested grid.

Report:

- full-grid WR median, minimum, maximum and interquartile range;
- full-grid Total R median, minimum and maximum;
- count and percentage of combinations with positive Total R;
- count and percentage above the existing 60% descriptive reference.

No new threshold is inferred from the observed maximum.

### S2 — Baseline locality

For each of the four parameters, compare the baseline against its two one-parameter neighbors while holding the other three parameters fixed.

Report absolute WR change, Total R change and PF change.

A large discontinuity is a stability warning; a smooth change is stability evidence. The decision is descriptive unless a formal pre-registered threshold is applied.

### S3 — Temporal consistency

Use the four already observed weekly partitions exactly as stored in the matrix.

Report:

- weekly decisive WR for baseline;
- minimum weekly WR;
- maximum weekly WR;
- standard deviation across weekly WR;
- number of weeks above 60%.

Do not move week boundaries after seeing outcomes.

### S4 — Parameter main-effect sensitivity

For each parameter, aggregate the matrix by level and report the distribution at each level.

This is a sensitivity diagnostic, not an optimization procedure.

Because the grid is observational and the same historical sample is reused, no causal interpretation is allowed.

### S5 — Multiple-testing guard

Do not treat the highest-performing combination as a discovery.

The 81-combination search space is explicitly acknowledged as a multiple-comparison surface. Any production parameter must come from source evidence / previously frozen rules, not from selecting the best matrix result.

### S6 — Statistical uncertainty

For the baseline decisive WR, report a descriptive 95% Wilson interval.

The archived four-week baseline artifact contains trade-level observations for all four weekly partitions: 158 trades total, with 154 decisive outcomes and 4 AMBIGUOUS outcomes. AMBIGUOUS observations must remain excluded from the decisive-WR numerator and denominator; they must not be reassigned to WIN or LOSS.

Where implemented, an additional time-preserving block/bootstrap analysis may be applied to these archived baseline outcomes. Any resampling result applies only to the observed baseline sample and must not be generalized to the 81-combination grid.

Do not interpret either interval or resampling result as an out-of-sample guarantee or as proof of independent Bernoulli trials. Trade dependence, market-regime dependence and execution assumptions remain limitations.

The 81-combination matrix contains aggregate combination-level results rather than trade-level outcomes for every combination. Therefore no trade-level bootstrap/permutation test may be claimed for the complete 81-point surface from that matrix alone.

## Gate interpretation

The stability gate has three possible dispositions:

- **POSITIVE EVIDENCE:** the declared surface shows no material isolated-performance dependency within the tested range and no unexplained discontinuity in the declared checks.
- **INCONCLUSIVE:** evidence is mixed, sample limitations prevent a reliable disposition, or an intended check cannot be computed from the archived data.
- **NEGATIVE EVIDENCE:** a material instability or concentration is identified under the pre-registered checks.

A POSITIVE disposition does not authorize production.

## Fresh Holdout boundary

The untouched holdout remains frozen at:

**2026-09-19 00:00:00 UTC**

Frozen configuration:

- XAUUSD.ecn
- M1
- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R

No parameter tuning is permitted using holdout observations.

## Current disposition

The existing 81-point matrix already provides positive robustness evidence. This protocol formalizes the next stability assessment without changing the strategy.

The current production gate remains **BLOCKED** because:

1. Frozen Geometry is still blocked.
2. The matrix is not untouched validation.
3. The Fresh Holdout has not yet received eligible post-boundary bars.
4. Live execution remains disabled.

## Canonical-rules guard

This document does not:

- promote any parameter combination;
- change P-Gap;
- define AB=CD;
- define fill behavior;
- authorize BUY/SELL generation;
- enable live trading.

