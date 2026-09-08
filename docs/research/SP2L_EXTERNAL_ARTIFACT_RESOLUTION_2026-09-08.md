# SP2L External Artifact Resolution — 2026-09-08

## Objective
Evaluate whether the publicly documented TradingFinder SP2L implementation provides enough additional geometry to freeze Strategy A without overriding the authoritative source video.

## Evidence hierarchy
1. Authoritative Poursamadi source video/transcript.
2. Source visual frames.
3. Official Poursamadi material.
4. Secondary implementation/artifact documentation (TradingFinder).
5. Deterministic specification.
6. Backtest results.

## External artifact inspected
TradingFinder's MT4 SP2L Poursamadi page documents an indicator based on Spike + 2-Leg/AB=CD and publishes chart/settings screenshots. The page states that the script is an implementation/tool and provides explicit implementation claims about spike structure, entry, SL and TP.

Relevant observations:
- It describes a three-candle aligned spike construction, with the middle candle representing imbalance and a gap between the first and third candles.
- It states a 65% minimum body-to-total-size condition and a configurable spike-size threshold.
- It describes entry after price retraces and breaks the last spike candle; the XAUUSD screenshot labels a breakout/entry level and a signal-closing candle.
- It places SL at the lowest point of the spike leg / starting point of wave A for bullish examples and mirrors this for bearish examples.
- It uses entry-to-SL distance for a 1:1 TP.
- Its published settings screenshot exposes only a candle-count input for spike moving-average and a spike-size percentage input; the implementation is protected/closed and therefore its internal code is unavailable.

## Critical source-alignment assessment
These details are useful as external hypotheses but are NOT promoted to canonical Strategy A rules.

### Potentially corroborative
- Spike-origin structure is used for SL.
- A first directional wave is used for the 2-leg projection.
- 1:1 TP is consistent with the primary source's explicit TP1 preference.
- Entry is structurally associated with a prior spike candle/level.

### Not canonical / remains rejected or unresolved
- Generic three-candle FVG interpretation.
- 65% body ratio.
- Any numeric spike-size threshold.
- Fixed three-candle spike index.
- Entry = break of last spike candle.
- Classical A/B/C labeling from the external implementation.
- Any closed-source Gap Filter formula.

## Important discrepancy
The external implementation describes an entry after a retrace/break of the last spike candle, while the authoritative source video explicitly describes placing a manual or pre-set limit during the correction and shows a Buy Limit. Therefore the external implementation cannot replace the source's pending-limit execution semantics.

## P-Gap conclusion
The external artifact does NOT expose a source-authoritative P-Gap formula. Its public text uses FVG/imbalance terminology and its code is protected. Consequently:

`P-Gap = generic FVG` remains unproven and is not frozen.

The strongest source-aligned meaning remains:

`valid breakout/spike context + source-defined P-Gap/non-overlap`

with exact OHLC boundaries, candle timing, equality/touch semantics, and minimum-size threshold unresolved.

## Entry conclusion
The external artifact strengthens the hypothesis that entry is tied to a prior spike candle's structural level, but it does not prove the universal candle identity or exact OHLC field required by Strategy A. The authoritative source's pending-limit semantics remain primary.

Strongest candidate:
- BUY: relevant/prior Low -> Buy Limit.
- SELL: relevant/prior High -> Sell Limit.

## SL conclusion
The external artifact independently corroborates the source meaning that SL is structurally beyond the candle/low-high from which the spike originates. Exact executable price remains unresolved (wick/body, strictness, buffer).

## Gate decision
This external artifact materially improves the evidence map but does NOT satisfy Frozen Geometry.

SOURCE RESOLUTION: advanced.
FROZEN GEOMETRY: BLOCKED.
DEV: locked.
VAL: untouched.
FRESH HOLDOUT: untouched.
PRODUCTION: unchanged.

## Next action
Do not reverse-engineer protected code or infer hidden formulas. Freeze only semantic contracts that have authoritative support. If an original source-provided template, settings export, or openly published source implementation becomes available, use it as a new evidence artifact; otherwise preserve the remaining geometry as unresolved.
