# SP2L G36 — Source Geometry Resolution Run

Date: 2026-09-09
Status: SOURCE-RESOLUTION PASS / EXECUTABLE GEOMETRY STILL BLOCKED

## Scope

This pass is source-first. It does not use profitability, optimization, or backtest performance to decide what the source means.

## Evidence consolidated

### P-Gap
The source explicitly associates a valid breakout with P-Gap and distinguishes P-Gap from generic gap categories. Multiple source examples show separation associated with breakout/follow-through, including variants where the gap presentation occurs at different points in the sequence.

Decision: **SEMANTICALLY CONFIRMED; EXACT OHLC FORMULA UNRESOLVED.**

Rejected canonical shortcut: generic three-candle FVG/imbalance.

### Entry
The source explicitly demonstrates a pending Limit / Buy Limit during correction. The entry line is distinct from the structural stop and, in repeated examples, tracks a relevant completed structural Low/High as the correction develops.

Decision: **PENDING-LIMIT SEMANTICS CONFIRMED; UNIVERSAL OHLC ANCHOR UNRESOLVED.**

No assumption that Entry equals original Spike extreme, Leg-2 start, body edge, wick extreme, or Fibonacci retracement.

### Structural invalidation / SL
The source explicitly separates Entry from SL and describes structural invalidation/order management.

Decision: **STRUCTURAL INVALIDATION CONFIRMED; EXACT OHLC ANCHOR UNRESOLVED.**

Risk percentage is sizing input, not the source definition of invalidation.

### Trigger
Source examples explicitly contain one-, two-, and three-candle trigger constructions and key-bar examples. A trigger can activate the pending-limit setup.

Decision: **TRIGGER FAMILY CONFIRMED; ACCEPTANCE/TIMING RULE UNRESOLVED.**

Market close-reclaim is not promoted as equivalent.

### AB=CD
The source explicitly writes AB=CD and links the second leg magnitude to the first leg magnitude. Competing wick/body/structural-pivot interpretations can all satisfy the visible relationship.

Decision: **MAGNITUDE RELATIONSHIP CONFIRMED; A/B/C/D ANCHORS AND TOLERANCE UNRESOLVED.**

No Fibonacci substitution is made.

### Leg 2 / TP
The source explicitly discusses first leg, second leg, pullback toward the start of Leg 2, TP1/TP2 and 2X. TP1 is preferred in the teaching; TP2 is presented as larger/researchable.

Decision: **CONCEPTS CONFIRMED; EXECUTABLE PROJECTION FORMULA UNRESOLVED.**

### Pending-order replacement
The source permits deletion/replacement when the evolving structure materially changes the risk distance. The exact numerical/algorithmic threshold is not source-defined.

Decision: **QUALITATIVE RULE CONFIRMED; THRESHOLD UNRESOLVED.**

## Source-resolution decision rule

If two or more candidate geometries remain consistent with authoritative source evidence, the result remains UNRESOLVED. Synthetic fixtures can eliminate candidates that violate explicit evidence, but cannot manufacture source uniqueness.

## Gate result

- SOURCE RESOLUTION: **PARTIAL PASS**
- SYNTHETIC FIXTURES: **PASS / ONGOING**
- FROZEN GEOMETRY: **BLOCKED**
- DEV: LOCKED
- UNTOUCHED VALIDATION: LOCKED
- ROBUSTNESS/STABILITY: LOCKED
- FRESH HOLDOUT: LOCKED
- PRODUCTION: LOCKED

## Next source action

The next useful source action is not optimization. It is targeted extraction of the highest-information chart frames for each unresolved geometry, followed by side-by-side candidate overlays and explicit source-uniqueness tests. If ambiguity survives, retain UNRESOLVED rather than inventing a rule.
