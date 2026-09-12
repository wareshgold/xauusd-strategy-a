# SP2L G263 — Measurement Label Cross-Reference

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `MEASUREMENT_MAPPING_STRONGLY_CORRELATED__EXECUTION_SEMANTICS_UNRESOLVED`

## Objective

Cross-reference the recurring source labels `0.0`, `2x`, `E`, `1`, and `2` against practical order examples and the clean SP2L schematic without turning visual/numerical correlation into an unsupported execution rule.

## Evidence set

### Practical order example — ~21:40

Visible row:

- Price/Entry: `3229.08`
- S/L: `3237.12`
- T/P: `3213.44`

On the chart, the measurement labels appear in the same vertical construction as:

- `0.0` at the stop-side reference;
- `2x` between the stop-side reference and `E`;
- `E` at the entry-side reference;
- `1` and `2` progressively on the target side.

Numerically, `3237.12` and `3229.08` are separated by `8.04`, and their midpoint is `3233.10`. The visual `2x` marker lies approximately at that midpoint. This is strong independent support for the **measurement-label relationship**, not a proof of how Entry or SL were originally constructed.

The practical T/P `3213.44` is close to the displayed `2` level, but it is not exactly the simple 2R projection from the visible Entry/SL pair (`3229.08 - 2×8.04 = 3213.00`). The 0.44 difference must not be explained by an invented tolerance, spread, rounding rule, or target-selection rule.

### Multi-order example — ~23:40

Visible rows include:

- `3229.08 / 3237.12 / 0.00`
- `3223.84 / 3235.50 / 3213.33`
- `3228.88 / 3235.50 / 0.00`

The chart simultaneously shows recurring `0.0`, `2x`, `E`, `1`, and `2` labels associated with the measurement construction(s). Multiple execution rows are present, so the screenshot does **not** establish that one single target label applies identically to every row.

This is an important negative result: the measurement vocabulary is reusable, while terminal execution semantics remain underdetermined.

### Clean source schematic — ~42:50–43:20

The source explicitly labels `Entry`, `SL`, `TP1`, and `TP2`. The vertical drawing shows TP1 approximately one Entry→SL risk interval above Entry and TP2 approximately two such intervals above Entry. This is strong schematic geometry.

However, the schematic does not state that:

- `TP1` is always the terminal target;
- `TP2` is always the terminal target;
- `2` is always TP2;
- `AB=CD` terminates at TP2;
- a practical order must use the schematic target exactly.

## Cross-reference result

The strongest defensible interpretation is:

`0.0` → stop-side reference  
`E` → Entry reference  
`2x` → midpoint-style measurement marker between stop-side reference and Entry  
`1`, `2` → successive target-side measurement levels

The source repeatedly correlates these labels with the Entry/SL construction. The correlation is strong enough to document as source vocabulary, but not enough to freeze the underlying OHLC construction or terminal TP rule.

## Non-inferences explicitly rejected

- `E = correction low/high`;
- `E = C`;
- `E = P-Gap boundary`;
- `0.0 = exact wick/body boundary`;
- `2x = an independently defined trade rule`;
- `1 = mandatory TP1 execution`;
- `2 = mandatory TP2 execution`;
- practical TP = exact 2R;
- any 0.44-style difference is spread/rounding/tolerance;
- one measurement object maps to every visible order row.

## Decision

`MEASUREMENT VOCABULARY: SOURCE-CORRELATED`  
`ENTRY/SL CONSTRUCTION: UNRESOLVED`  
`TERMINAL TP SELECTION: UNRESOLVED`  
`PRODUCTION: BLOCKED`
