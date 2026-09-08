# SP2L Leg-1 Origin Resolution — 2026-09-08

**Branch:** `research/pgap-source-resolution-v1`  
**Gate:** SOURCE RESOLUTION  
**Status:** research-only; production unchanged

## Objective

Resolve whether source-level Leg 1 should be measured from:

1. the Spike-origin candle to the Spike extreme;
2. the breakout candle/level to the Spike extreme; or
3. the first structural Low/High to the Spike extreme.

The decision must come from source evidence, not historical profitability.

## Source evidence

The source explicitly defines SP2L as Spike → 2Leg and introduces `AB=CD`. At the candle-level discussion it contrasts the taught method with classical internet AB=CD/Fibonacci treatment. It then states that after the Spike a correction is expected and the next leg should be the same size as the first leg.

The real XAUUSD section around 62:00–65:00 shows the bearish case being evaluated candle-by-candle, including a pronounced directional move, correction, later continuation and target/order management. The visual material supports a leg-to-leg measurement concept, but the rasterized chart does not expose a defensible exact OHLC anchor for the first leg.

The earlier interpretation of small chart annotations as classical A/B/C/D labels has been explicitly superseded; those marks are not reliable evidence for harmonic anchors.

## Discrimination result

### Candidate A — Spike-origin → Spike-extreme

**Status: STRONGEST SOURCE-ALIGNED CANDIDATE; NOT FROZEN.**

Reason: the source separately identifies the candle from which the Spike originated for structural SL placement, and repeatedly describes the first/second legs as the movement produced by the Spike and its continuation. This gives the cleanest candle-level interpretation without importing external swing logic.

### Candidate B — breakout candle/level → Spike-extreme

**Status: PLAUSIBLE CANDIDATE; NOT DISCRIMINATED.**

Reason: the source tightly associates valid breakout/P-Gap with the Spike. However, no direct statement was found that defines Leg 1 as beginning at the breakout level rather than at the Spike-origin structure.

### Candidate C — first structural Low/High → Spike-extreme

**Status: PLAUSIBLE CANDIDATE; NOT DISCRIMINATED.**

Reason: the source uses candle-level Low/High language for correction and entry. But that does not establish that the same structural point is the Leg-1 origin.

## Critical finding

The source evidence does **not** safely collapse these three concepts into one anchor:

`Spike origin ≠ proven breakout anchor ≠ proven correction/entry anchor`

Therefore no deterministic A/B/C/D mapping is introduced.

## Synthetic fixture matrix

| Fixture | Purpose | Required conclusion |
|---|---|---|
| L1-O01 | Origin candle and breakout candle have different prices | keep A vs B distinguishable |
| L1-O02 | First structural Low/High differs from origin | keep A vs C distinguishable |
| L1-O03 | Same visual Spike, different candidate origins | no backtest-based selection |
| L1-O04 | Deep correction changes entry level but not Spike movement | Leg 1 must not silently become a retracement measurement |
| L1-O05 | Bullish mirror of L1-O01 | direction symmetry required |
| L1-O06 | Bearish mirror of L1-O02 | direction symmetry required |
| L1-O07 | Equal visual leg but different candle endpoints | exact OHLC anchor remains unresolved |

## What is now safe to encode semantically

`source-defined Spike movement → source-defined first-leg magnitude → correction → second leg of equal magnitude`

This is a semantic invariant, not an executable formula.

## Explicitly forbidden imports

- classical harmonic A/B/C/D anchors;
- generic swing-high/swing-low algorithms;
- Fibonacci retracement ratios;
- choosing the origin that maximizes backtest performance;
- using the P-Gap boundary as Leg-1 origin without direct evidence;
- assuming the entry price is the Leg-1 endpoint;
- inventing an AB=CD tolerance.

## Gate decision

**Leg-1 source resolution: PARTIAL.**

- Source semantic of equal first/second legs: **SOURCE-CONFIRMED**
- Spike-origin → extreme: **STRONGEST CANDIDATE**
- Breakout → extreme: **UNRESOLVED CANDIDATE**
- Structural Low/High → extreme: **UNRESOLVED CANDIDATE**
- Exact executable Leg-1 OHLC anchor: **UNRESOLVED**
- AB=CD tolerance: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- DEV / VAL / Fresh Holdout: **LOCKED**
- Production: **UNCHANGED**

## Next action

Do not backtest these alternatives yet. The next source-resolution target is the **exact P-Gap candle boundary/timing**, because it may discriminate the breakout-associated candle sequence and thereby narrow the Leg-1 origin without importing external geometry.
