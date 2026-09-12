# SP2L G265 — Order Panel Numeric Reconstruction

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `NUMERIC_CORRELATION_CONFIRMED__EXECUTION_MAPPING_UNRESOLVED`

## Purpose

Reconstruct the visible order-panel examples numerically and cross-reference them with the source measurement labels `0.0 / 2x / E / 1 / 2` without promoting any unproven price formula.

## Source visual evidence

Primary visual evidence:

- `order_21_40.png` — practical order panel around 21:40.
- `order_23_40.png` — practical order panel around 23:40.

## Example A — visible order row

| Field | Value |
|---|---:|
| Entry / Price | 3229.08 |
| S/L | 3237.12 |
| T/P | 3213.44 |
| Current price shown | 3224.67 |

Risk distance:

`3237.12 - 3229.08 = 8.04`

Midpoint between S/L and Entry:

`3229.08 + 8.04 / 2 = 3233.10`

The `2x` measurement line in the visual is positioned at the corresponding midpoint. This is strong evidence that `2x` is a midpoint-style measurement marker for the displayed stop/entry interval.

## Example B — multiple visible order rows

| Row | Entry | S/L | T/P |
|---|---:|---:|---:|
| 1 | 3229.08 | 3237.12 | 0.00 |
| 2 | 3223.84 | 3235.50 | 3213.33 |
| 3 | 3228.88 | 3235.50 | 0.00 |

For row 2:

`risk = 3235.50 - 3223.84 = 11.66`

`midpoint = 3223.84 + 11.66/2 = 3229.67`

The visual placement of the `2x` marker is consistent with a midpoint interpretation, but the terminal T/P is not equal to a simple 2R projection from that row:

`3223.84 - 2*11.66 = 3200.52`

versus visible T/P `3213.33`.

## Deterministic findings

1. The practical panel supplies real numerical Entry, S/L and T/P values.
2. `2x` is strongly correlated with the midpoint of the S/L↔Entry interval.
3. `E` is strongly correlated with the Entry reference.
4. The target-side labels `1` and `2` are distinct measurement references in the source visual.
5. A visible T/P cannot be derived as simple `Entry ± 2*Risk` for all observed rows.
6. No source statement authorizes a tolerance that would reconcile the discrepancy.

## Non-inferences

- `E = C` is not established.
- `E = correction Low/High` is not established.
- `2 = terminal T/P` is not established.
- `T/P = 2R` is not established.
- `T/P = AB=CD endpoint` is not established.
- Any spread, rounding, slippage, partial-close or broker-execution adjustment is not established.

## Gate decision

The numeric examples strengthen the **measurement-vocabulary layer**, but they do not freeze the executable Entry or terminal-target construction.

`SOURCE RESOLUTION: PASS_PARTIAL`  
`FROZEN GEOMETRY: BLOCKED`
