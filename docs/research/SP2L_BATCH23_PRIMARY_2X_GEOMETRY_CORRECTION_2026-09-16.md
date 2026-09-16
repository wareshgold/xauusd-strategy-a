# SP2L Batch 23 — Primary 2X Geometry Evidence Correction — 2026-09-16

## Purpose

This batch performs a falsification-oriented recheck of the earlier F13 claim that the primary diagram proves a 50% midpoint relation. The project rule is that source meaning outranks apparent geometric similarity; therefore the diagram is re-read conservatively.

## Recheck target

Frame around 2520 seconds shows handwritten `Buy`, `2X`, and `SL` annotations on a bullish schematic. There are horizontal levels and vertical arrows indicating distances, but the sampled image is not a calibrated price plot and the drawn pixel distances are not demonstrably equal.

The direct evidence therefore supports:

- `2X` is explicitly taught and visually placed between the Buy level and SL in the schematic.
- Buy, 2X, and SL are distinct instructional levels in this diagram.

The evidence does **not** by itself prove:

- exact 50% price-distance equality;
- a formula such as `2X = Entry + 0.5*(SL-Entry)`;
- whether `Buy` is intended entry, filled entry, or pending-order level in this diagram;
- order type, trigger, fill, sizing, cancellation, or replacement semantics.

The account-table worked example also contains multiple entries with different stop distances, so it cannot be used to infer a unique 2X formula from the annotation.

## Corrected F13 evidence status

**SOURCE-CONFIRMED CONCEPT / 2X LEVEL RELATION VISUALLY DEMONSTRATED / EXACT PRICE FORMULA AND EXECUTION SEMANTICS UNRESOLVED.**

The previously used phrase "primary geometric midpoint evidence" is too strong unless supported by a source statement or calibrated numerical example. This correction deliberately downgrades that wording and prevents the visual sketch from becoming a canonical 50% rule.

## Implementation impact

- No code changed.
- No backtest changed.
- No canonical 2X formula introduced.
- No production logic introduced.
- 125R remains untouched.

## Gate

Frozen Geometry remains BLOCKED.
