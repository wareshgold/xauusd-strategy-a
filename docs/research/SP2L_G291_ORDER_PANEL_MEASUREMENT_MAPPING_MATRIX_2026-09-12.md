# G291 — Order Panel / Measurement Mapping Matrix

Date: 2026-09-12

## Purpose
Cross-check the worked order-panel prices against the visible `0.0 / 2x / E / 1 / 2` measurement construction without assigning unsupported semantics.

## Repeated source geometry

The worked chart repeatedly displays:

- `0.0` on the stop-side reference;
- `2x` between `0.0` and `E`;
- `E` at/near the Entry reference;
- `1` and `2` on the target side.

Across the reviewed states, `2x` is visually located approximately halfway between the stop-side `0.0` reference and `E`. This supports the interpretation that the labels form a measurement construction, but it does not identify the measured quantity.

## Numeric cross-check

### State A
- Entry = 3229.08
- SL = 3237.12
- stop-side distance = 8.04
- midpoint = 3233.10
- observed `2x` position is consistent with that midpoint
- TP = 3213.44
- Entry→TP = 15.64

### State B
- Entry = 3223.84
- SL ≈ 3235.50 (the order panel shows the same stop region in the later state)
- stop-side distance ≈ 11.66
- midpoint ≈ 3229.67
- TP = 3213.33
- Entry→TP = 10.51

### State C
- Entry = 3228.88
- SL = 3235.50
- stop-side distance = 6.62
- midpoint = 3232.19
- TP = 3213.45
- Entry→TP = 15.43

## Mapping conclusions

| Item | Source evidence | Safe status |
|---|---|---|
| `0.0` is stop-side reference | repeated visual/order construction | strong |
| `E` is Entry-side reference | repeated visual/order construction | strong |
| `2x` is a midpoint-like construction | numeric cross-check in multiple states | strong correlation |
| `1` and `2` are target-side references | repeated visual construction | strong |
| `1 = 1R` | not explicitly established | unresolved |
| `2 = 2R` | not explicitly established | unresolved |
| `2 = terminal TP` | not explicitly established | unresolved |
| target ladder is Leg-1 projection | source concepts suggest this, but bridge is not explicit in this slice | unresolved |
| target ladder is AB=CD | AB=CD is source-confirmed, but anchor mapping is unresolved | unresolved |

## Decision
`MEASUREMENT_MAPPING = PARTIALLY_RESOLVED`

The measurement convention is real source evidence. Its semantic role is not yet sufficiently specified to implement a canonical target engine.

## Fail-closed rule
Research may calculate candidate interpretations for `1/2`, Leg 1, AB=CD and target selection. Production may not select among them until an authoritative source bridge fixes the anchor and equation.
