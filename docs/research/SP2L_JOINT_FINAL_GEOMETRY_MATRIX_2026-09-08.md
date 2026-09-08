# SP2L Joint Final Geometry Matrix — 2026-09-08

## Objective

Resolve the remaining relationship among P-Gap, Entry, SL and Leg-1 across the source's bullish and bearish constructions without importing third-party or classical harmonic geometry.

Evidence hierarchy remains:

1. authoritative source video/transcript;
2. source visual frames;
3. official-source corroboration;
4. secondary implementation descriptions;
5. deterministic specification;
6. research/backtest.

## Source-frame pass

The source frames around 34:00–36:40 show three accepted-looking constructions and one rejected construction. The slide explicitly states `Valid BO = P-Gap`. Blue/grey highlighted regions are visible, but their boundaries cannot be mapped uniquely to a single OHLC boundary pair. The same pass therefore cannot distinguish wick-to-wick, body-to-body, or a specific High/Low pair with sufficient source certainty.

The clean entry diagram around 46:00–46:40 shows separate horizontal levels for Entry, TP1, TP2 and SL. The Entry level is visually distinct from the P-Gap illustration and the SL is structurally below the early/origin portion of the bullish movement. The exact candle OHLC price represented by the Entry and SL lines remains visually underdetermined.

Real-chart frames around 49:00–52:30 contain management/context annotations and shaded regions, but do not expose a machine-readable exact P-Gap boundary or A/B/C/D mapping. They are corroborative only.

## Joint resolution matrix

| Component | Source-confirmed meaning | Strongest candidate | Must remain unresolved |
|---|---|---|---|
| P-Gap | breakout-associated gap/non-overlap validating the breakout/spike | wick-range non-overlap in breakout context | exact boundary pair, candle timing, equality/touch, minimum size |
| Entry BUY | correction reaches prior/relevant Low; pending limit in spike direction | immediately preceding/relevant candle Low | universal candle identity, wick/body convention, buffer |
| Entry SELL | correction reaches prior/relevant High; pending limit in spike direction | immediately preceding/relevant candle High | universal candle identity, wick/body convention, buffer |
| SL BUY | structural invalidation beyond spike-origin candle | origin-candle Low reference | exact executable price, strictness, buffer |
| SL SELL | structural invalidation beyond spike-origin candle | origin-candle High reference | exact executable price, strictness, buffer |
| Leg 1 | first source-defined directional leg magnitude | spike-origin → spike-extreme | exact OHLC anchors, wick/body convention |
| Leg 2 | second leg continues with source-confirmed equal/approximately equal magnitude | correction anchor ± Leg1 magnitude | correction anchor, equality tolerance |
| AB=CD | named source relationship, candle-level rather than imported classical harmonic construction | equal directional magnitudes | A/B/C/D anchors and tolerance |

## Critical separation

The evidence supports the following dependency graph:

`Range/context → valid breakout + P-Gap → Spike → correction → relevant prior Low/High → pending-limit entry`

and independently:

`Spike-origin candle → structural invalidation / SL`

and:

`source-defined Leg 1 magnitude → source-defined Leg 2 equal-magnitude projection`

No evidence establishes a direct identity between P-Gap boundary, Entry price, SL price, or classical A/B/C/D points.

## Cross-direction check

Bullish and bearish source semantics mirror cleanly:

- BUY correction references Low;
- SELL correction references High;
- BUY SL is beyond origin Low;
- SELL SL is beyond origin High.

This symmetry is source-aligned semantically, but it does not resolve the exact candle index or OHLC field.

## Frozen candidates vs unresolved geometry

The following may be treated as semantic contracts in research code:

- P-Gap must be source-confirmed; generic FVG is not sufficient.
- Entry must be represented as a pending limit, not a close-reclaim substitute.
- Entry and P-Gap are distinct concepts.
- SL must reference the spike-origin structure.
- Leg-2 projection must use the source-defined Leg-1 magnitude relationship.
- Classical harmonic A/B/C/Fibonacci anchors are not imported.

The following must NOT be frozen yet:

- `P-Gap = previous High < next Low` or any other exact formula;
- generic three-candle FVG;
- fixed entry candle index;
- `entry = C`;
- `entry = 50% retracement`;
- exact SL wick/body/buffer;
- fixed Leg-1 OHLC endpoints;
- numerical AB=CD tolerance.

## Gate decision

SOURCE RESOLUTION: **substantially advanced**.

FROZEN GEOMETRY: **still BLOCKED** by exact P-Gap geometry and executable price conventions.

DEV: **locked**.

UNTouched VAL / Fresh Holdout: **locked and untouched**.

PRODUCTION: **unchanged**.

## Next discriminating action

Do not backtest these unresolved candidates. The highest-information next action is to seek a source artifact that exposes the exact P-Gap/Entry/SL price boundaries (e.g. an original chart/template or source-provided indicator settings/code). If no authoritative artifact exists, freeze only the semantic contracts above and explicitly leave executable geometry unresolved.
