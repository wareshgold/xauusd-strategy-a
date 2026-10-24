# SP2L Temporal / Rolling Stability Results — 2026-09-19

## Scope
Research-only temporal stability analysis of the frozen 2026-09-14 through 2026-09-18 historical signal window.

This analysis does not modify geometry, execution semantics, parameters, or canonical rules.

## Results

### Daily decomposition

| UTC day | Decisive | Wins | Losses | WR | Net pips | PF |
|---|---:|---:|---:|---:|---:|---:|
| 2026-09-14 | 9 | 9 | 0 | 100.00% | +326.5 | N/A |
| 2026-09-15 | 13 | 9 | 4 | 69.23% | +230.3 | 3.015 |
| 2026-09-16 | 3 | 2 | 1 | 66.67% | +36.1 | 3.959 |
| 2026-09-17 | 5 | 4 | 1 | 80.00% | +45.4 | 1.599 |
| 2026-09-18 | 7 | 3 | 4 | 42.86% | +5.1 | 1.047 |

The daily view is heterogeneous and sample sizes are small. 2026-09-18 is the weakest day by win rate, but it remains slightly positive in net pips and PF.

### Rolling 10-decisive-trade windows

- 28 overlapping windows.
- WR range: 60.00%–90.00%.
- Mean window WR: 72.14%.
- Net pips range: -3.2 to +291.3.
- 27/28 windows positive.
- 1/28 windows non-positive.
- PF range: 0.978–9.276.

Therefore the rolling-10 surface is broadly positive but not uniformly positive.

### Rolling 15-decisive-trade windows

- 23 overlapping windows.
- WR range: 60.00%–86.67%.
- Mean window WR: 71.88%.
- Net pips range: +62.1 to +474.0.
- 23/23 windows positive.
- PF range: 1.310–9.089.

This is a stronger descriptive stability surface than rolling-10, but the windows overlap heavily and are not independent observations.

## Gate assessment

**Temporal Stability Gate: INCONCLUSIVE — NO PASS / NO FAIL**

Rationale:
1. The chronological surface does not show a sustained collapse: rolling-15 windows remain positive.
2. There is still meaningful short-window variation, including a 42.86% day and one rolling-10 window with -3.2 pips.
3. Daily sample sizes range from only 3 to 13 decisive trades.
4. Rolling windows overlap, so 28 and 23 windows must not be treated as independent statistical trials.
5. The historical window is not a fresh post-boundary holdout.

## What this does NOT establish

- It does not prove a stable live edge.
- It does not resolve P-Gap, AB=CD, swing/SL, trigger, pending-order, or fill semantics.
- It does not justify parameter promotion.
- It does not authorize live trading.
- It does not convert the research harness into canonical Strategy A.

## Current project state

- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Parameter Robustness: POSITIVE research evidence
- Parameter Stability: INCONCLUSIVE
- Temporal/Rolling Stability: INCONCLUSIVE
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Production Authorization: BLOCKED
- Live Trading: DISABLED

## Next evidence requirement

The next meaningful gate is not another optimization pass on this same historical week. The priority is an eligible **fresh post-boundary MT5 holdout** after 2026-09-19 00:00:00 UTC, using the frozen research configuration, once the MT5 data becomes available.

Guard: RESEARCH_TEMPORAL_STABILITY_ONLY; NO_RULE_OR_PARAMETER_PROMOTION