# SP2L — Source Evidence Register

**Date:** 2026-09-07  
**Purpose:** Single durable register of source-grounded SP2L facts already established, so future research continues from evidence instead of re-asking the user.

## Authority rule

The original Pour Samadi source material is the semantic authority. This register records only evidence already established from the source and project research. Missing numeric geometry remains **TBD**. Historical performance must never be used to invent or redefine source semantics.

## Source evidence already established

### 1. SP2L lifecycle

The source-supported lifecycle currently used for research is:

`CONTEXT / RANGE -> STRONG MOVE / BREAKOUT FAMILY -> FOLLOW-THROUGH / KEY-BAR BEHAVIOR -> SPIKE FAMILY -> STRUCTURAL LOW/HIGH SEQUENCE -> CORRECTION -> PENDING LIMIT -> PRICE TOUCH / FILL -> STRUCTURAL INVALIDATION / STOP -> LEG 2 -> TP1`

This is a research semantic model, not yet production/live execution logic.

### 2. Pending-limit entry

The demonstrated SP2L examples use a pending limit order during the correction. The entry is not canonically defined as a close-reclaim market entry.

Current research candidate:
- bullish: selected HL/reference low -> BUY LIMIT;
- bearish: selected LH/reference high -> SELL LIMIT;
- activation: price touch of the pending level.

Exact universal HL/LH selection algorithm and validity duration remain candidate/TBD.

### 3. Structural stop

The source establishes a structural stop/invalidation concept and describes the stop in relation to the candle/point where the spike originates.

Current research candidate:
- bullish spike: structural stop around spike-origin low;
- bearish spike: structural stop around spike-origin high.

Exact universal reference and any buffer are TBD. No ATR/points/ticks/percentage/spread buffer has been assumed.

### 4. Leg 1 / Leg 2

The source explicitly distinguishes the first directional leg from the second directional leg after correction and uses the relationship that Leg 2 is approximately equal to Leg 1.

The exact machine-readable endpoints are **not yet resolved**.

Current status:
- Leg1 endpoint A/B: **TBD**;
- Leg2 projection origin C: **TBD**;
- numerical equality tolerance: **TBD**.

Do not invent ±5%, ±10%, ±20%, ATR, tick, point, or fixed-distance tolerances.

### 5. Nested legs / 2X

The source demonstrates nested SP2L structures and separately discusses 2X. Therefore 2X must not be silently merged into the base Position-1 / TP1 model.

Research state currently keeps `position2xEnabled = false` until independently resolved.

### 6. P-GAP / gap context

The gap lesson establishes that gap interpretation is contextual, not merely candle geometry.

Source-grounded distinctions:
- P-GAP = pressure/continuation evidence in the appropriate structural context;
- exhaustion gap = late-move/exhaustion evidence and can support exit/reversal interpretation;
- session/time and market location matter;
- a visible gap alone is insufficient to create an SP2L signal.

Exact P-GAP geometry, size threshold, candle-count/overlap rules, session windows, location threshold, and exhaustion decision tree remain TBD.

### 7. Break + gap simultaneous event

**Source visual evidence around 37:22:** the supplied source image explicitly shows a break from a level occurring simultaneously with a gap.

Recorded semantic fact:

`LEVEL BREAK + GAP can occur in the same transition/event.`

Important boundary: the image does **not** establish a universal mathematical gap formula, minimum gap size, wick/body rule, overlap threshold, or required candle count. None is inferred from the image.

The user explicitly clarified that this is the exact image at 37:22 and that the lesson moves to the next topic immediately afterward. This evidence should not be requested again.

### 8. Session/location discipline

The source material repeatedly conditions gap interpretation on time/session and market location. A visually similar gap at an arbitrary time/location is not automatically the same semantic object.

Therefore gap detection must carry contextual metadata before classification.

## Research decisions already frozen

1. Source semantics outrank existing implementation behavior.
2. Existing close-reclaim entry is not treated as canonical SP2L semantics.
3. Existing production Strategy A code is not a source authority.
4. Historical DEV/VAL results cannot define what a source term means.
5. Fresh Holdout remains locked until the candidate semantics are frozen and survive DEV -> VAL -> robustness review.
6. No guessed P-GAP formula is allowed.
7. No guessed Leg1/Leg2 endpoint formula is allowed.
8. No fitted Leg2 equality tolerance is allowed.
9. 2X remains separate from base SP2L Position 1.
10. Same-candle ambiguity must be represented explicitly rather than resolved optimistically.

## Evidence locations in the repository

- `docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`
- `docs/research/PHASE_31_SP2L_GEOMETRY_RESOLUTION_PROTOCOL.md`
- `docs/research/PHASE_31_SP2L_SOURCE_EXCAVATION_V3.md`
- `docs/research/PHASE_32_SP2L_V2_SEMANTIC_STATE_AND_FIXTURES.md`
- `docs/research/PHASE_33_G2_PENDING_LIMIT_RESOLUTION.md`
- `docs/research/PHASE_33_G3_STRUCTURAL_STOP_RESOLUTION.md`
- `docs/research/PHASE_33_G4_LEG1_SOURCE_RESOLUTION.md`
- `docs/research/PHASE_33_G6_LEG2_EQUALITY_SEMANTICS.md`
- `docs/research/PHASE_33_G7_SP2L_EXECUTION_SEMANTICS.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_GAP_GEOMETRY_RESEARCH_V1_2026-09-05.md`

## Future-agent instruction

Before asking the user to repeat any already-established SP2L source detail, read this register and the Strategy A Poorsamadi Knowledge Map. If a rule is not explicitly resolved here or in the source-grounded documents, mark it **TBD** and continue research rather than asking the user to restate known evidence.

## Current gate

SP2L research can continue through source-grounded semantic fixtures and non-production analysis. Canonical historical validation and live implementation remain blocked until the unresolved G4/G5 geometry is recovered and frozen with source provenance.
