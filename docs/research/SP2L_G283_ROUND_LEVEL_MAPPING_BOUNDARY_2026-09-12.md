# SP2L G283 — Round Level Mapping Boundary

Date: 2026-09-12
Status: SOURCE-CONFIRMED CONCEPT / EXECUTION SEMANTICS UNKNOWN

## Evidence

The primary target-construction sequence visibly includes `Round level 2` and handwritten examples around `2500`, `3200`, `3250`, and `3255`.

## What is source-confirmed

- Round-level terminology is used by the source.
- Round-level discussion occurs in the same target-construction sequence as TP1/TP2/Entry/SL.

## What remains unresolved

The source evidence does not uniquely define:

- what `Round level 2` means operationally;
- the increment or granularity of a round level;
- whether round level selects Entry, TP1, TP2, or provides context;
- nearest/next/previous/manual selection;
- tie-breaking;
- relationship between round level and the 250/500 point annotations;
- relationship between round level and AB=CD.

## Implementation rule

No canonical `round_level()` target selector may be implemented from these frames alone. Research fixtures may enumerate candidate interpretations, but production must remain fail-closed.

`ROUND_LEVEL_CONCEPT = CONFIRMED`
`ROUND_LEVEL_SELECTOR = UNKNOWN`
`ROUND_LEVEL_INCREMENT = UNKNOWN`
`ROUND_LEVEL_POINT_RELATION = UNKNOWN`
