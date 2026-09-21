# SP2L F10 Stop-Loss Case Study — 2026-09-21

## Status

- Research-only evidence
- Canonical: **false**
- Frozen Geometry: **BLOCKED**
- Purpose: document one completed demo-forward case and compare alternative SL distances without promoting a trading rule.

## Observed case

Source execution log:
- Symbol: XAUUSD.ecn
- Side: BUY
- Theoretical entry: 4346.90
- Research SL used: 4344.87
- Observed risk distance: 2.03
- TP at 1R: 4348.93
- Research SL anchor: SPIKE_CANDLE_EXTREME_RESEARCH
- Execution mode: PENDING_LIMIT_RESEARCH

Subsequent MT5 M1 observation:
- Sample window: six hours ending at the audit time
- Bars: 360
- Observed high: 4383.42
- Observed low: 4345.80
- Last close: 4351.79

## Counterfactual SL scenarios

Assuming XAUUSD pip convention of 0.01 for this research comparison:

| SL | Risk distance | 1R TP from 4346.90 | Observed M1 path reached TP level? |
|---|---:|---:|---|
| 50 pip | 0.50 | 4347.40 | Yes |
| 60 pip | 0.60 | 4347.50 | Yes |
| 70 pip | 0.70 | 4347.60 | Yes |
| 80 pip | 0.80 | 4347.70 | Yes |
| Existing | 2.03 | 4348.93 | Yes |

The observed six-hour M1 range alone does not establish intratrade sequencing for every level. It only establishes that these prices occurred within the sampled window. The observed low was 4345.80, which is 1.10 below entry.

## Interpretation

This case is evidence that the chosen research SL distance materially affected the 1R target distance in this particular trade.

It does **not** establish:
- that 50–80 pips is the teacher's canonical stop distance;
- that pip size/convention should be frozen as a Strategy A rule;
- that a wider SL would necessarily have avoided the actual stop event without changing order timing or lifecycle;
- that the same SL distance generalizes across setups.

The source-resolution requirement remains: F10 must be resolved from source evidence for the exact stop field, any buffer, and invalidation event. Performance must not select the canonical stop.

## Forward-test handling

The existing clean forward test was not restarted after this observation. The old forward test remains untouched.

This case is archived as a research input for F10 resolution only.
