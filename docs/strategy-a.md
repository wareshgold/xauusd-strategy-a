# Strategy A / SP2L — Source-Aligned Semantic Contract

> **Status: SEMANTIC CORE FROZEN. FROZEN GEOMETRY: BLOCKED.**
>
> This document records only what the current authoritative source corpus supports. It is **not** an executable trading specification. Any item marked `UNRESOLVED` or `NON-CANONICAL` must not be promoted by backtest performance.

## 1. Identity

**Strategy A = SP2L (Spike → 2 Leg).**

The authoritative material describes a sequence of power/spike, correction, and continuation toward a second leg.

## 2. Source-confirmed semantic core

The following concepts are source-supported:

- market context / range;
- breakout and follow-through;
- Spike as a directional price movement;
- a valid Spike/breakout associated with **P-Gap / Pressure Gap**;
- correction following the first movement/leg;
- pending-limit entry during the correction;
- structural invalidation / stop behind the Spike-origin candle/structure;
- second-leg continuation;
- approximately equal Leg 1 and Leg 2 magnitude;
- explicit **AB = CD** relationship;
- entry direction follows the Spike direction;
- TP1 is described as the default/primary target in the public source material;
- a secondary 50% entry concept exists in the official page, but its mandatory core scope is unresolved;
- context/location and higher-timeframe alignment are described as favorable conditions, not as fully specified executable filters.

## 3. P-Gap

**Semantic status: RESOLVED.** P-Gap is the Pressure Gap concept used in the SP2L material.

**Executable status: UNRESOLVED.** The current authoritative corpus does not provide enough evidence to freeze all numerical geometry required by an algorithm.

Still unresolved:

- exact OHLC endpoints;
- wick/body treatment;
- minimum size;
- overlap rules;
- tolerance;
- exact candle-count/sequence requirement;
- a universal formula mapping the generic gap example to P-Gap.

**Explicit prohibition:** the generic three-candle gap formula from the separate gap lesson must not be silently promoted as the P-Gap formula.

## 4. Spike / breakout / follow-through

The source supports a directional Spike, breakout/follow-through context, and the relationship between Spike and P-Gap.

The following executable details remain unresolved:

- exact candle-strength threshold;
- minimum movement size;
- maximum width;
- fixed candle count;
- exact breakout boundary;
- exact follow-through threshold;
- universal anti-channel/cleanliness formula.

No numerical threshold is canonical unless source-confirmed.

## 5. Correction and structural sequence

The source supports a correction after the first movement/leg and describes corrective price reaching the prior candle's low in an uptrend or high in a downtrend.

The source also shows nested/deeper leg examples and order movement during a correction.

Unresolved:

- the canonical algorithm for selecting the first important High/Low;
- minimum/maximum correction depth;
- parent-vs-nested leg selection;
- fixed candle-count requirements;
- exact state transition from correction to trigger.

## 6. AB = CD / Leg 1 / Leg 2

**Semantic status: RESOLVED.** The source explicitly presents **AB = CD** and describes the next leg as approximately the same size as the first leg.

**Executable anchor status: UNRESOLVED.** The current source corpus does not uniquely define machine-readable A/B/C/D anchors in every case.

Therefore the following are prohibited as canonical rules until source-confirmed:

- arbitrary A/B/C/D candle indices;
- body-only or wick-only anchor selection;
- fixed tolerance around equality;
- substituting an invented `Entry + Leg1` formula for the source's AB=CD geometry;
- selecting parent or nested scale by backtest performance.

## 7. Entry

**Mechanism: RESOLVED.** The source explicitly supports placing a **pending buy/sell limit order during the correction**, including pre-setting the limit order.

**Exact price/fill semantics: UNRESOLVED.** The source corpus does not uniquely establish:

- exact limit-price formula;
- whether the order price is an A/B/C/D point or another structural level;
- whether a geometric point called C is identical to fill price;
- partial-fill behavior;
- intrabar fill ordering when multiple levels are crossed;
- cancellation/replacement semantics as correction evolves.

Do not replace the pending-limit mechanism with a market-close/reclaim rule.

## 8. Stop / invalidation

**Semantic status: RESOLVED.** The official source describes the stop as being behind the candle/structure from which the Spike originated, and the video describes cancellation when price returns to the invalidation area.

**Exact boundary: UNRESOLVED.** No canonical offset, wick/body convention, or exact inclusive/exclusive boundary is currently source-confirmed.

## 9. Targets

The source supports a primary TP1 concept and gives 1:1 as the default on the official page; the video also discusses TP1/TP2 and 2X/3X as options/examples.

**Canonical mapping: UNRESOLVED.** The corpus does not establish a single machine-readable TP formula that reconciles all target descriptions with the AB=CD geometry.

Therefore fixed 2R/3R targets must not be promoted as Strategy A geometry.

## 10. Secondary 50% entry / 2X

The official page documents a secondary entry at 50% of the entry-to-SL distance. The video separately discusses 2X as a money-management/execution option.

**Core-scope status: UNRESOLVED.** These concepts must remain separate from the canonical setup detector until their exact source-defined role is established.

## 11. Context and time

The source identifies important levels, channel edges, higher-timeframe alignment, and higher-volume/NY conditions as favorable context.

These are not frozen as hard filters. In particular, the following must remain non-canonical unless independently source-confirmed:

- EMA-60 rules;
- round-number spacing rules;
- fixed London/Frankfurt/New York session windows;
- generalized M1/M5 filters;
- arbitrary minimum RR filters.

## 12. Canonicality rule

A concept is canonical only when both are true:

1. authoritative evidence supports its meaning; and
2. the executable geometry required to implement it deterministically is resolved.

Otherwise it remains `canonical=false` / `UNRESOLVED` and may be investigated only in the hypothesis layer.

## 13. Production gate

Current gate state:

```text
SOURCE RESOLUTION (current primary corpus): COMPLETE
        ↓
SEMANTIC CORE: FROZEN
        ↓
FROZEN GEOMETRY: BLOCKED
        ↓
CANONICAL DEV: BLOCKED
        ↓
VAL / ROBUSTNESS / FRESH HOLDOUT: NOT STARTED
        ↓
PRODUCTION: BLOCKED
```

Historical profitability must never be used to decide what an unresolved source concept means.

## 14. Hypothesis boundary

Permitted research hypotheses include competing P-Gap geometry, A/B/C/D anchors, parent/nested leg selection, limit-price semantics, fill semantics, stop boundary, and target mapping. Every such implementation must carry an explicit hypothesis ID and `canonical=false`.

The hypothesis layer may be tested on synthetic fixtures and historical data, but its results must not be presented as canonical Strategy A validation.
