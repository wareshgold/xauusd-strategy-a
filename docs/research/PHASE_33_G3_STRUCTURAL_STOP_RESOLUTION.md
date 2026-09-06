# Phase 33 — SP2L G3 Structural Stop Resolution

**Date:** 2026-09-06  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Candidate geometry resolution — research only

## Objective

Resolve the next SP2L geometry question:

> Where is the structural stop reference relative to the spike origin?

## Source evidence

Public SP2L descriptions consistently describe the stop as being placed behind the candle where the spike originated, usually the lowest point before a bullish sharp move or the highest point before a bearish sharp move. citeturn0search1turn0search4

The same descriptions identify the initial wave / point A as the stop reference and use the entry-to-stop distance for risk/reward calculation. citeturn0search4turn0search5

This supports the structural reference:

```text
BULLISH -> spike-origin candle LOW
BEARISH -> spike-origin candle HIGH
```

## G3 candidate

The research candidate therefore exposes the origin candle's directional extreme:

```text
Bullish stop candidate = origin candle low
Bearish stop candidate = origin candle high
```

The implementation intentionally returns `bufferStatus: TBD`.

It does **not** invent:

- pip/point/tick buffer;
- percentage buffer;
- ATR buffer;
- spread adjustment;
- broker-specific execution offset;
- candle-close vs intrabar stop-touch semantics.

## Important distinction

The source phrase "behind the origin" does not mean that the raw origin extreme is necessarily the final executable stop price.

Therefore we separate:

```text
SOURCE STRUCTURAL REFERENCE
origin candle extreme

from

EXECUTION STOP PRICE
origin extreme + directional buffer/execution policy
```

The first is a G3 candidate. The second remains unresolved.

## Deterministic fixture contract

The fixture suite requires:

- bullish -> origin low;
- bearish -> origin high;
- finite candle geometry;
- explicit `bufferStatus: TBD`;
- no hidden buffer;
- no historical optimization.

## Decision

**G3 structural reference candidate accepted for further source review.**

It is not yet a production stop rule and it is not used in historical backtests.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–32 reports remain immutable.
- Production Strategy A remains untouched.
- No EMA50/EMA100 rule is promoted.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result decides source meaning.

## Next step

G4 — resolve the exact Leg 1 endpoints and distinguish the structural AB reference from the stop reference.
