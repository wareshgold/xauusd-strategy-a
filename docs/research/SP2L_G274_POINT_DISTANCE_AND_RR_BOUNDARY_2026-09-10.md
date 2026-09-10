# SP2L G274 — Point Distance vs R-Multiple Boundary

Date: 2026-09-10
Status: SOURCE-CONFIRMED VOCABULARY / EXECUTION MAPPING UNRESOLVED

## Evidence

Primary video target-construction sequence around 44:00–44:40 visibly contains the annotations `250 point` and `500 point` while the TP1/TP2 schematic is displayed.

Earlier order-panel evidence provides concrete Entry/SL/TP values where simple 2R does not always reproduce the displayed TP.

## Decision

The source supports investigating a point-distance target convention in addition to risk-distance notation. It does NOT yet prove that:

- TP1 = Entry + 250 points
- TP2 = Entry + 500 points
- point means broker tick/point, 0.01 price unit, or another source-specific unit
- the point distances are universal constants
- point-distance is the terminal TP selector
- point-distance replaces AB=CD

These remain hypotheses until the source explicitly connects the handwritten numbers to a price example or order construction.

## Required next evidence

Find a source sequence containing both:

1. a concrete Entry/SL price scale or price labels, and
2. explicit application of the 250/500 point distances to TP1/TP2.

Without that bridge, keep point-distance as a source-confirmed concept but not a deterministic execution rule.

## Gate

`POINT_DISTANCE_CONCEPT = SOURCE_CONFIRMED`
`POINT_UNIT = UNKNOWN`
`POINT_DISTANCE_TARGET_FORMULA = UNKNOWN`
