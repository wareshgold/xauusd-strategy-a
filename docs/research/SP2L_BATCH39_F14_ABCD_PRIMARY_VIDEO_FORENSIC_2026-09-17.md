# SP2L Batch 39 — F14 AB=CD Primary-Video Forensic

Date: 2026-09-17

## Purpose

Resolve F14 using the primary SP2L training video after the author-owned Python implementation was found and cross-checked in Batch38.

## Primary-video evidence inspected

Focused window: approximately 36:00–46:00 of the uploaded SP2L training artifact, with finer inspection around 36:10–39:00 and 42:00–45:30.

### AB=CD is explicitly written

Around the 36:30–37:30 section, the SP2L Strategy slide is annotated with `AB=CD`. The same slide also contains `1M` and `5M` annotations.

This is direct primary-artifact evidence that AB=CD is part of the taught SP2L framework.

### The visual concept is two corresponding directional legs

The handwritten drawings show an initial directional movement, a corrective movement, and a subsequent directional movement. The AB=CD annotation is attached to this structure.

This supports the conceptual interpretation that the two directional legs are intended to have an equality relationship.

### Exact A/B/C/D price anchors are not explicitly readable

The inspected primary frames do not provide a readable textual definition such as:

- A = exact wick low/high
- B = exact wick high/low
- C = exact correction endpoint
- D = exact continuation endpoint
- body-vs-wick choice
- close-vs-touch requirement
- numerical equality tolerance
- minimum/maximum deviation from equality

Therefore no numeric AB=CD tolerance is frozen.

### AB=CD does not appear as an explicit computation in the inspected author Python bot

Repository search did not expose an `AB=CD` implementation in the inspected SP2L Python implementation/notebook search surface. The author bot therefore cannot be used to manufacture A/B/C/D anchors or tolerance.

### TP geometry is shown separately later in the video

Around 45:10–45:40, the worked diagram explicitly labels `SL`, `Entry`, `TP1`, and `TP2`. The vertical distance from Entry to TP1 is drawn as a risk-distance relationship, while TP2 is a further target. This supports the existence of separate TP1/TP2 concepts in the primary artifact.

This does not by itself override the author-associated page's default 1:1 TP statement or establish a universal TP2 rule; exact target lifecycle remains a separate source-resolution item.

## F14 status after Batch39

**SOURCE-CONFIRMED CONCEPT / EXACT ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED**

The project may record `AB=CD` as a canonical concept, but must not encode an invented numeric formula or tolerance.

## Important consequence for the project path

The author implementation plus primary video now reduce the major unknowns substantially:

- P-Gap: exact author implementation geometry is known for both directions.
- Spike: exact fixed local candle window and body-comparison family are known in author implementation.
- Trigger: immediate local low/high break and pending->entry state are known in author implementation and conceptually source-aligned.
- SL: origin-candle reference is known in author implementation and source-aligned.
- Secondary entry: 50% of entry-to-SL distance is source-confirmed and implemented.
- AB=CD: concept is source-confirmed, but exact computational anchors/tolerance remain unresolved.
- Round Level: still unresolved as an exact algorithm.

## Gate

No canonical geometry freeze is performed in Batch39.

## Next action

Perform one focused Round Level forensic pass and one final source-to-code reconciliation for the remaining unresolved execution semantics. If no new source contradiction appears, construct a **research-only author-replication candidate** from the author implementation and run it on the project's untouched data without promoting it to canonical. This separates two questions:

1. Can the author's implementation reproduce a positive historical edge?
2. Are the exact rules source-confirmed enough to become the project's canonical Strategy A?

The first question is useful for profitability research; the second remains the production gate.
