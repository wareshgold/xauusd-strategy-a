# G280 — Target Geometry Gate

Date: 2026-09-10

## Gate result
`BLOCKED__TARGET_GEOMETRY_NOT_FROZEN`

## Confirmed source concepts
- Entry, TP1, TP2, SL appear together in a source construction schematic.
- Round Level is explicitly discussed in the same construction sequence.
- Point Distance is explicitly discussed, with 250 point and 500 point examples.
- AB=CD is explicitly source-confirmed elsewhere in the SP2L material.
- Pending-limit entry and structural stop semantics remain source-confirmed from earlier gates.

## Still unresolved
- exact Entry price anchor;
- exact SL OHLC boundary;
- exact A/B/C/D anchors;
- exact Leg-1 measurement anchor;
- exact Leg-2 projection equation;
- exact mapping of 250/500 point to TP1/TP2;
- exact Round Level selection rule;
- terminal TP selector;
- SELL mirror geometry;
- units/rounding/tick/spread semantics;
- intrabar/close execution semantics.

## Gate policy
No historical optimization, performance result, or convenient implementation may resolve these unknowns. Synthetic hypothesis fixtures are permitted only for falsification/clarification and remain research-only.

## Next source-resolution target
Locate a worked source example with a continuous chain:
`setup → Entry → SL → measured Leg 1 / AB=CD → TP1/TP2`,
preferably with an explicit numeric price or stated point/round-level operation. If the source never provides this bridge, preserve UNKNOWN rather than inventing a rule.
