# Phase 33 G4 — SP2L Leg 1 Source Resolution

**Date:** 2026-09-06
**Branch:** `research/phase12-preentry-geometry-robustness`
**Status:** Research-only — exact executable Leg 1 endpoints remain TBD

## Objective

Resolve the semantic meaning of SP2L Leg 1 from the preserved Poorsamadi source before introducing any historical backtest rule.

## Source evidence reviewed

The preserved `POORSAMADI_SP2L_SOURCE.txt` explicitly states that SP2L is named from **Spike → 2 Leg**, and that after a spike the expected correction should lead to a second leg whose magnitude is approximately equal to the first leg.

At approximately **36:59**, the source states that after a spike the expectation is a correction followed by completion of Leg 2, with Leg 1 and Leg 2 becoming equal.

At approximately **1:02:41–1:03:32**, the bearish examples describe a sequence of lower highs, distinguish a first leg from a subsequent second leg, and explicitly treat the visible movement as nested leg structures rather than one undifferentiated wave.

At approximately **1:04:00–1:04:32**, the source describes waiting for a deep leg, identifies a sequence of lower highs, places an order, waits for activation, and then says that the first leg was from one chart location to another. The transcript text does not encode the visual coordinates of those two locations.

## What is source-established

1. SP2L contains a first directional leg and a second directional leg.
2. Leg 2 is expected to approximately match Leg 1 in magnitude.
3. The source reasons about legs using candle-by-candle structure and identifiable structural movement.
4. Lower-high / higher-low sequences can define meaningful directional structure.
5. The source contains examples where a leg can itself contain a nested SP2L structure; therefore leg boundaries must be tied to the intended scenario, not blindly to the entire visible move.

## What the transcript does NOT establish numerically

The raw transcript does not provide machine-readable coordinates for the phrases equivalent to “from here to here”. The source text therefore cannot uniquely distinguish among these endpoint candidates:

- first structural low/high → spike extreme;
- spike origin → spike extreme;
- relevant candle open → spike extreme;
- structural point → structural point;
- another source-specific A/B pair visible only in the chart image.

Selecting one solely because it produces the strongest historical result would violate the source-first research protocol.

## Important correction to prior assumptions

The existing Strategy A `LegProjection` implementation uses an implementation-defined Leg 1 endpoint model. That implementation is **not evidence of Poorsamadi's intended geometry**.

Likewise, the current correction extreme must not automatically be treated as the Leg 2 projection origin until source evidence resolves that question.

## G4 decision

**G4 CORE CONCEPT: SOURCE-CONFIRMED.**

**G4 EXACT ENDPOINTS: UNRESOLVED / TBD.**

No executable Leg 1 formula is promoted.

No production code is changed.

No historical DEV/VAL search is performed to select endpoints.

Fresh Holdout remains locked.

## Required next evidence

The next useful source evidence is visual rather than textual: the chart screenshots/frames corresponding to the source examples around:

- 36:59–37:22
- 1:02:41–1:03:32
- 1:04:00–1:04:32

Those frames are required if we want to resolve the exact A/B coordinates faithfully rather than infer them.

## Next step

Do **not** implement a G4 Leg 1 calculator yet.

Resolve the visual A/B endpoints first. Once those are source-resolved, create deterministic positive/negative fixtures and only then proceed to G5 (Leg 2 projection origin).

## Guardrails

- Production Strategy A untouched.
- Existing baseline reports untouched.
- Phase13–30 results remain immutable.
- Fresh Holdout remains locked.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical outcome used to define source semantics.
