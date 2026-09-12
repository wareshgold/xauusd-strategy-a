# SP2L G324 — Visual Numeric Bridge Audit: 250 / 500 / 1000

**Date:** 2026-09-12  
**Status:** `STRONG_VISUAL_MAPPING__EXPLICIT_ASSIGNMENT_STILL_UNCONFIRMED`

## Source frame inspected

Primary SP2L source frame supplied in the project evidence set: target-construction frame around 44:20.

The frame visibly contains four ordered horizontal levels:

`TP2 > TP1 > Entry > SL`

The vertical ruler shows three consecutive intervals. Visual pixel inspection confirms the three intervals are approximately equal in the schematic. This is stronger than a qualitative impression of an arbitrary ladder.

The same frame contains handwritten annotations:

- `250 point` adjacent to the upper target portion;
- `500 point` adjacent to the lower target/order portion;
- the surrounding source sequence also contains `1000`.

## Strongest source-consistent reconstruction

The geometry is internally consistent with:

```text
SL ───── 500 ───── Entry ──250── TP1 ──250── TP2
<---------------------- 1000 -------------------->
```

Under this reconstruction:

- Entry → TP1 = 250 points;
- TP1 → TP2 = 250 points;
- Entry → TP2 = 500 points;
- SL → Entry = 500 points;
- SL → TP2 = 1000 points.

This reconstruction explains both the equal-interval schematic and the three handwritten magnitudes without requiring a geometrically inconsistent ladder.

## Critical source boundary

The frame does **not** contain a sufficiently explicit arrow, equation, or written sentence assigning each handwritten quantity to a specific interval. Therefore this is not promoted to canonical executable geometry.

The correct evidence classification is:

`C1 = STRONGEST SOURCE-CONSISTENT HYPOTHESIS`

not:

`C1 = FROZEN RULE`.

## Worked-order reconciliation boundary

The earlier worked order panels contain different Entry prices with clustered terminal TP values. Those examples reject a universal final-entry-based `TP = Entry ± 2R` rule, but they do not by themselves prove the 250/500/1000 mapping above. The source schematic and live order examples must therefore remain separate evidence classes until a continuous numeric bridge is found.

## Non-inferences

Do not infer from this frame alone:

- instrument tick/point conversion for XAUUSD;
- that 250 points is always TP1 distance;
- that 500 points is always TP2 distance;
- that 1000 is always SL→TP2;
- a universal fixed-point target engine;
- any SELL mirror;
- rounding, spread, or execution semantics;
- that the schematic is an executable order example rather than an explanatory construction.

## Decision

`VISUAL_EQUAL_INTERVAL = STRONGLY_SUPPORTED`
`C1_MAPPING = STRONGEST_HYPOTHESIS`
`EXPLICIT_NUMERIC_ASSIGNMENT = NOT_PROVEN`
`FROZEN_TARGET_FORMULA = BLOCKED`
