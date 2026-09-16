# SP2L Source Resolution Matrix — F8–F16 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F16** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction and primary-artifact micro-forensic passes. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE + WORKED-EXAMPLE EVIDENCE / REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER + WORKED-EXAMPLE EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + BETWEEN-LEVEL VISUAL RELATION / EXACT PRICE FORMULA AND EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT EXPLICIT AB=CD / CONCEPT CONFIRMED / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT BEARISH EXECUTION CONFIRMED / EXACT MIRROR GEOMETRY UNRESOLVED** | No | BLOCKED |
| F16 | Round level | **SOURCE-CONFIRMED CONCEPT / MULTIPLE SPACING CANDIDATES OBSERVED / EXACT ROUND-LEVEL ALGORITHM UNRESOLVED** | No | BLOCKED |

## Batch 23 — F13 evidence-boundary correction

A falsification-oriented recheck of the primary 2X schematic around frame 2520 found that `Buy`, `2X`, and `SL` are explicitly marked and that 2X is visually placed between the Buy and SL levels. However, the schematic is not a calibrated price plot and the drawn pixel distances are not demonstrably equal. The account-table examples also contain multiple entries with different stop distances.

Therefore the earlier wording "primary geometric midpoint evidence" is withdrawn as too strong. The source-supported statement is narrower:

**2X is explicitly taught as a distinct level positioned between Buy and SL in the schematic; the exact 50%-distance price formula is unresolved.**

No canonical 2X formula, order type, trigger, fill, sizing, cancellation, or replacement semantics is introduced.

## Batch 24 — F16 round-level forensic update

Primary frames around **2640–2670 (~44:00–44:30)** visibly annotate **"Round level"** and show price examples around the 3200/3250/3255 area. A following frame visibly includes spacing annotations **"250 point"**, **"500 point"**, and **"1000"**.

This strengthens the source evidence that round-number levels and multiple spacing magnitudes are part of the teaching/context. It does **not** uniquely establish the instrument scale, whether these are exact point/tick increments or presentation shorthand, which spacing is selected, the rounding anchor, proximity threshold, or whether round level acts as a filter, score feature, entry condition, or contextual annotation.

The research-only synthetic fixture records `[250, 500, 1000]` as observed candidates without selecting a canonical interpretation.

## Batch 25 — F8/F12/F16 chain forensic update

A dense primary-artifact sequence was inspected for the proposed chain:

**structural level → valid BO / P-Gap → pending Buy Limit → execution**, with Round Level as a possible contextual predecessor.

Observed evidence:

- Around frame **2280 (~38:00)** the primary slide explicitly states **"Valid BO = P-Gap"** beside a bullish candle sequence.
- Around frame **2310 (~38:30)** several local lower points are marked on the bullish sequence.
- Around frame **2340 (~39:00)** multiple horizontal reference levels are drawn, with a **BO** annotation and a **Buy Limit** annotation introduced in the same teaching sequence.
- Around frame **2370 (~39:30)** a horizontal level is explicitly labeled **"Buy Limit"**.
- Around frame **2400 (~40:00)** the horizontal order line remains extended through the sequence.
- Around frames **2430–2460 (~40:30–41:00)** order-management annotations include **delete**.
- Around frames **2640–2670 (~44:00–44:30)** Round Level and multiple spacing examples are taught separately.

The individual concepts are therefore strongly source-supported. The artifact does **not** uniquely establish that Round Level is a required predecessor of the specific Buy Limit, nor does it uniquely map a particular marked low to the Buy Limit price. The numeric P-Gap formula and exact breakout/order activation semantics are also absent from this sequence.

Therefore the complete chain remains:

**SOURCE-CONFIRMED CONCEPT CHAIN / EXACT EXECUTABLE MAPPING UNRESOLVED.**

No canonical swing selection, P-Gap formula, Round Level algorithm, Buy Limit price construction, fill semantics, or order lifecycle rule is introduced.

## F14 / F15 current evidence boundary

F14 remains explicitly supported at the concept level by the handwritten `AB=CD` teaching sequence around frames 2190–2220, while A/B/C/D anchor semantics and equality/tolerance remain unresolved.

F15 remains directly supported by the bearish/sell-side worked episode around frames 3510–3630, while the exact mathematical mirror of bullish executable geometry remains unresolved.

## Gate decision

**Source Resolution: PARTIAL PASS — individual concepts and their teaching sequence strengthened; executable chain remains unresolved.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production implementation was changed.
