# SP2L G325 — Worked Order vs Schematic Reconciliation

**Date:** 2026-09-12  
**Status:** `SCHEMATIC_MAPPING_STRONG__WORKED_ORDER_NUMERIC_BRIDGE_NOT_ESTABLISHED`

## Objective

Test whether the source schematic's 250/500/1000 quantities can be directly mapped onto the previously captured worked order prices.

## Worked order observations

Example A:

- Entry = 3229.08
- SL = 3237.12
- TP = 3213.44
- SL→Entry = 8.04 price units
- Entry→TP = 15.64 price units
- Reward/R ≈ 1.945

Example B:

- Entry = 3223.84
- SL ≈ 3235.50
- TP ≈ 3213.33
- SL→Entry ≈ 11.66 price units
- Entry→TP ≈ 10.51 price units
- Reward/R ≈ 0.901

These examples do not share a common final-entry-to-target ratio.

## Result

The worked orders cannot be used to prove that the handwritten `250 point`, `500 point`, and `1000` values are literal price distances in those orders.

Likewise, the worked orders do not provide enough evidence to determine the instrument-specific definition of `point` used in the educational schematic.

## Important distinction

The source schematic can therefore be treated as **construction evidence**, while the worked order panels are **execution/example evidence**. They should not be merged into one formula unless the source explicitly connects them.

The discrepancy is not treated as a contradiction in the source. It simply means that the numeric bridge between the schematic and the worked order examples has not been demonstrated.

## Rejected implementation shortcut

Do not implement:

`TP = Entry ± 500 points`

or

`TP = Entry ± 2R`

or any fixed-point mapping solely because one interpretation fits the schematic.

## Decision

`WORKED_ORDER_BRIDGE = UNRESOLVED`
`POINT_UNIT = UNRESOLVED`
`FINAL_TP_FORMULA = UNRESOLVED`
`CANONICAL_TARGET_ENGINE = NOT_AUTHORIZED`
