# Phase 36 — SP2L G5 Candidate Discrimination Matrix

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Objective

Continue G5 without inventing the missing OHLC coordinate for the Leg 2 projection origin.

The source evidence already establishes that the parent Leg 2 follows the intervening/deep correction. The remaining question is which exact source-selected point inside that correction is C.

## Candidate matrix

| Candidate | Source compatibility | What current evidence actually proves | Current decision |
|---|---|---|---|
| `CORRECTION_EXTREME` | Possible | Leg 2 follows the deep/intervening correction | **Not canonical** — source does not explicitly equate “deep correction” with its absolute high/low |
| `STRUCTURAL_HL_LH` | Possible | Source repeatedly uses structural HL/LH sequencing and selected structural references | **Still viable** — exact C selection not exposed |
| `PENDING_LIMIT` | Possible as a related level, but not proven as C | Pending limit is created during correction and is later touched | **Not canonical** — execution level and projection origin are distinct concepts in the current source evidence |
| `ACTUAL_FILL` | Possible as an event location, but not proven as C | Fill occurs when price touches the pending level | **Not canonical** — fill is an execution event, not automatically a geometric definition of Leg 2 origin |
| `OTHER_VISUAL_POINT` | Possible | Source describes visually identified leg boundaries/points, but transcript text does not expose exact OHLC coordinate | **Still viable** — requires source visual discrimination |

## Eliminations justified without historical data

### 1. Fill cannot be silently promoted to C

The source distinguishes order placement/activation from the visual Leg 1 measurement and subsequent Leg 2 projection. Therefore `ACTUAL_FILL` must not be auto-populated as the Leg 2 origin.

### 2. Pending price cannot be silently promoted to C

A pending limit is an execution instruction. The fact that it is created during the correction does not prove that its price is the source's geometric C point.

### 3. Correction extreme cannot be promoted to C from the word “deep” alone

“Deep correction” establishes structural location, not the exact OHLC field or candle that defines C. Selecting the absolute correction extreme would add an algorithmic assumption not present in the recovered text.

## Candidates still alive

After source-only discrimination, the unresolved set is intentionally narrow:

1. `STRUCTURAL_HL_LH`
2. `OTHER_VISUAL_POINT`
3. potentially `CORRECTION_EXTREME`, but only if a source visual explicitly identifies the extreme as the projection origin

The last item is not eliminated universally; it is simply not established by transcript semantics alone.

## Required evidence for final G5 resolution

A source visual must answer at least one of these:

- Is C placed exactly on a visible HL/LH structural reference?
- Is C placed on the absolute correction extreme?
- Is C placed on the pending-limit level independently of the structural point?
- Is C another explicitly marked visual point?
- Does the same rule hold symmetrically for bullish and bearish examples?

Until one of these is recovered from source visual evidence, G5 remains:

```text
SEMANTIC RESOLVED / EXECUTABLE OHLC TBD
```

## Gate discipline

No DEV/VAL performance, Fresh Holdout, optimization, ATR, percentage, tick, point, spread, or fitted equality tolerance may be used to select C.

G6 remains blocked because equality cannot be validated until both Leg 1 endpoints and C are source-frozen.

## Next step

Proceed to source-visual discrimination of the C point. If no new visual evidence is recoverable, record G5 as unresolved rather than manufacturing a deterministic rule.