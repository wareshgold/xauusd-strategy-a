# Phase 33 G5 — SP2L Leg 2 Projection Origin Resolution

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — exact machine-readable projection origin remains TBD

## Objective

Resolve what the preserved Poorsamadi source actually establishes about the origin of Leg 2 without selecting a convenient projection point from historical performance.

## Source evidence

### 36:59–37:08

The source states that after a spike the expectation is a correction and then completion of the second leg, with Leg 1 and Leg 2 becoming equal in magnitude.

This establishes the ordering:

```text
SPIKE / LEG 1
  -> CORRECTION
  -> LEG 2
```

It does not uniquely encode the exact OHLC coordinate from which Leg 2 magnitude is projected.

### 37:57–38:18

The source again summarizes the sequence as a directional increase/decrease, then a correction, followed by the next leg of approximately equal size.

This reinforces that the correction separates Leg 1 from Leg 2.

### 1:02:41–1:03:32

The source discusses a bearish parent-leg example with nested 2Leg structure. It describes a first leg, a deep correction, and then the next leg. The wording around 1:03:19 explicitly treats the next leg as occurring from the correction region.

This is meaningful semantic evidence that the Leg 2 origin is tied to the completed/intervening correction rather than to an arbitrary unrelated point.

However, the transcript phrases the chart geometry visually (equivalent to "from here to here") and does not expose the exact price coordinate of the C point.

### 1:04:00–1:04:32

The source identifies a deep directional leg, several lower highs, order placement and activation, then points visually to the first-leg span and projected SP2L target.

Again, text confirms the conceptual A/B/C/D relationship but does not encode the exact chart coordinate for C.

## What is source-established

1. Leg 2 follows an intervening correction after Leg 1 / spike.
2. The correction is structurally meaningful; Leg 2 is not projected from an arbitrary pre-spike or unrelated price.
3. Leg 2 is expected to approximately match Leg 1 in magnitude.
4. Nested SP2L structures exist, so the projection origin must belong to the intended scenario/leg scale.
5. Candle-by-candle state must be respected; future candles cannot retroactively choose the correction point.

## What is NOT source-resolved from text

The preserved transcript does not uniquely establish whether the exact Leg 2 projection origin is:

1. the correction extreme;
2. the actual pending-limit fill price;
3. the selected structural low/high reference;
4. another visual C point used by Poorsamadi on the chart.

These candidates can coincide in some examples and differ materially in others. They must therefore remain separate.

## Important non-equivalences

The statement:

```text
Leg 2 begins after the correction
```

must NOT be silently rewritten as:

```text
Leg 2 origin = correction extreme
```

Likewise, the existence of a limit fill does NOT prove:

```text
Leg 2 origin = fill price
```

and the structural entry reference does NOT prove:

```text
Leg 2 origin = structural reference price
```

Those are implementation candidates, not source facts.

## G5 decision

**G5 SEMANTIC ORDERING: SOURCE-CONFIRMED.**

```text
LEG 1 -> CORRECTION -> LEG 2
```

**G5 EXACT PROJECTION ORIGIN: UNRESOLVED / TBD / VISUAL SOURCE REQUIRED.**

No canonical projection-origin formula is promoted.

No production code is changed.

No historical DEV/VAL search is allowed to choose the source meaning.

Fresh Holdout remains locked.

## Required next evidence

Visual chart frames corresponding to:

- 36:59–37:22
- 1:02:41–1:03:32
- 1:04:00–1:04:32

are the highest-value evidence for resolving the exact C coordinate.

## Next step

Keep G4 and G5 explicitly unresolved until visual A/B/C coordinates are source-resolved. Once resolved, create deterministic synthetic fixtures for the exact endpoint/origin mapping before chronological historical evaluation.

## Guardrails

- `STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md` is the current research synchronization map.
- Production Strategy A untouched.
- No source meaning selected by PnL.
- No threshold mining.
- No VAL/Fresh optimization.
- Fresh Holdout locked.
