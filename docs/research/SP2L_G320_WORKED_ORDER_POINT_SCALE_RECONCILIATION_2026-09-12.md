# SP2L G320 — Worked-Order Point-Scale Reconciliation

**Date:** 2026-09-12
**Status:** `DIRECT_SCALE_MAPPING_REJECTED__SOURCE_UNIT_SEMANTICS_UNRESOLVED`

## Objective

Test whether the source `250 point / 500 point / 1000` annotations can be directly mapped onto the previously captured worked order-panel prices.

## Worked examples

Example A:
- Entry = 3229.08
- SL = 3237.12
- TP = 3213.44
- Entry-to-TP absolute distance = 15.64
- SL-to-Entry distance = 8.04

Example B:
- Entry = 3223.84
- SL ≈ 3235.50
- TP ≈ 3213.33
- Entry-to-TP absolute distance ≈ 10.51
- SL-to-Entry distance ≈ 11.66

## Source schematic candidate

The strongest source-consistent candidate from G315/G316 is:

- Entry → TP1 = 250 points
- Entry → TP2 = 500 points
- SL → TP2 = 1000 points

This implies a schematic ratio of 500 : 250 : 250 for SL→Entry, Entry→TP1, TP1→TP2.

## Reconciliation result

The worked order examples do not expose a unique instrument-point conversion that makes the literal 250/500/1000 annotations equal to their displayed price distances. In particular, Example A has Entry→TP ≈ 15.64 while risk is 8.04; Example B has Entry→TP ≈ 10.51 while risk is ≈11.66.

Therefore the numeric annotations must not be treated as literal XAUUSD price-unit distances for these order-panel examples without additional source evidence.

## Important boundary

This does **not** reject the source schematic. It rejects only the unproven cross-example assumption that the handwritten 250/500/1000 values use the same executable price-point scale as the worked order panel.

Do not infer:
- 250 = fixed XAUUSD price distance;
- 500 = fixed XAUUSD price distance;
- 1000 = fixed XAUUSD price distance;
- a universal point-to-dollar conversion;
- TP = Entry ± 250/500 points;
- TP = 2R.

## Decision

`SCHEMATIC_RATIO = STRONG_VISUAL_EVIDENCE`
`WORKED_ORDER_LITERAL_POINT_MAPPING = REJECTED`
`POINT_UNIT_CONVERSION = UNRESOLVED`
`CANONICAL_TARGET_FORMULA = BLOCKED`
