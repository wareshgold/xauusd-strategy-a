# SP2L Working-Rules Experiment Contract — 2026-09-15

## Status

**NON-CANONICAL RESEARCH EXPERIMENT ONLY**

This contract freezes the analysis design before outcome statistics are inspected. It does not freeze Strategy A geometry, authorize execution, or generate production BUY/SELL decisions.

## Source / governance boundary

The source-confirmed dimensions remain limited to the adjudicated evidence packet. C03, C07, and C08 remain blocked. C02 and C05 are project-owner working hypotheses for this experiment, not source-confirmed canonical rules.

No experiment result may be used to retroactively define P-Gap geometry, entry/fill semantics, AB=CD anchors/tolerance, trigger classification, pending refresh thresholds, invalidation OHLC boundaries, or bearish symmetry.

## Fixed working hypotheses for this experiment

### C02 — risk/target test
- Initial SL hypothesis: **50–80 pips**.
- Initial target hypothesis: **1:2 risk/reward**.
- The experiment must preserve the 50, 60, 70, and 80 pip parameter points separately; they must not be silently pooled into one tuned value.
- Pip-to-price conversion is an explicit parameter and must not be invented from an undocumented broker/execution convention. If the dataset/source contract does not define the conversion, the run is blocked rather than guessed.

### C05 — market-direction filter
- Timeframe: **M15**.
- Direction hypothesis: bullish when price is above MA50; bearish when price is below MA50.
- MA50 calculation convention must be declared before measurement and kept fixed. No optimization of MA length or timeframe is permitted in this experiment.
- This is a research filter, not canonical source geometry.

## Event-layer restrictions

The event layer may only consume already-adjudicated source observations and the fixed working hypotheses above.

The following remain intentionally absent:

- canonical P-Gap OHLC formula
- exact candle indexing
- exact correction-entry anchor
- exact Leg-2 start anchor
- exact structural invalidation boundary
- exact pending-order fill/delete/replace semantics
- AB=CD A/B/C/D anchor definitions
- AB=CD tolerance
- deterministic trigger classifier for 1/2/3-candle constructions
- deterministic bearish mirror mapping

Therefore this experiment may produce **candidate observational statistics**, but may not emit executable signals.

## Outcome labeling

A candidate observation may be labeled only against a pre-declared, non-optimized outcome definition. The intended research target is a fixed 1:2 RR test under the selected SL parameter point.

If a required price-level or fill convention is not source-confirmed or explicitly fixed by the project owner, the observation is marked **UNRESOLVED**, not force-labeled.

No look-ahead is permitted. Labels must use only candles strictly after the candidate observation point.

## Parameter discipline

Primary parameter grid:

- SL: 50, 60, 70, 80 pips
- RR: 2.0R
- MA timeframe: M15
- MA length: 50

The four SL values are a pre-declared sensitivity grid, not four opportunities to select the best result.

## Required report fields

Every run must record:

- dataset SHA-256
- source metadata
- coverage start/end
- M1 and derived M5 counts
- experiment contract identifier/hash
- parameter grid
- candidate observation count
- resolved outcome count
- unresolved/excluded count and reasons
- win/loss/timeout counts where applicable
- win rate
- average R
- expectancy in R
- profit factor where defined
- maximum drawdown in R where defined
- per-parameter results
- no optimization decision

## Statistical interpretation guardrail

No minimum sample-size threshold, significance threshold, confidence interval method, or acceptance criterion is invented by this document. Those belong to the statistical validation contract and must be explicitly approved before any claim of edge.

A positive result is exploratory evidence only. It cannot resolve source ambiguity.
