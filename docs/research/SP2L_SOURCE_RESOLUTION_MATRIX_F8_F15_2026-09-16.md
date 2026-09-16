# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction and F14/F15 micro-forensic inspection. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

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

## Batch 23 — F13 evidence-boundary correction

A falsification-oriented recheck of the primary 2X schematic around frame 2520 found that `Buy`, `2X`, and `SL` are explicitly marked and that 2X is visually placed between the Buy and SL levels. However, the schematic is not a calibrated price plot and the drawn pixel distances are not demonstrably equal. The account-table examples also contain multiple entries with different stop distances.

Therefore the earlier wording "primary geometric midpoint evidence" is withdrawn as too strong. The source-supported statement is narrower:

**2X is explicitly taught as a distinct level positioned between Buy and SL in the schematic; the exact 50%-distance price formula is unresolved.**

No canonical 2X formula, order type, trigger, fill, sizing, cancellation, or replacement semantics is introduced.

## F14 / F15 current evidence boundary

F14 remains explicitly supported at the concept level by the handwritten `AB=CD` teaching sequence around frames 2190–2220, while A/B/C/D anchor semantics and equality/tolerance remain unresolved.

F15 remains directly supported by the bearish/sell-side worked episode around frames 3510–3630, while the exact mathematical mirror of bullish executable geometry remains unresolved.

## Gate decision

**Source Resolution: PARTIAL PASS — strengthened, with F13 wording conservatively corrected.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production implementation was changed.
