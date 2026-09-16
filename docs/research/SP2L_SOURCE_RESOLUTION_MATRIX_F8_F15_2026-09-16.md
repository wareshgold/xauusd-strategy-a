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
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + PRIMARY GEOMETRIC MIDPOINT EVIDENCE / EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT EXPLICIT AB=CD / CONCEPT CONFIRMED / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT BEARISH EXECUTION CONFIRMED / EXACT MIRROR GEOMETRY UNRESOLVED** | No | BLOCKED |

## Batch 22 — primary F14/F15 micro-forensic update

### F14 — AB=CD

Frames around approximately 36:30–37:00 (2190–2220) directly show the handwritten `AB=CD` annotation on the SP2L teaching slide. The same teaching sequence visibly contains `Valid BO = P-Gap`. Later worked diagrams around 45:30–47:00 distinguish the first/second-leg structure and separately label `Entry`, `TP1`, `TP2`, and `SL`.

This strengthens and clarifies the source-level concept: AB=CD/two-leg symmetry is explicitly taught. It still does not uniquely identify A/B/C/D candle indices, wick/body/OHLC component selection, projected versus observed D, equality versus another ratio/normalization, or numeric tolerance/rounding. No executable AB=CD formula is frozen.

### F15 — bearish mirror / execution

The worked material around 12 May 2025 contains a direct sell-side episode. Frame 3510 shows a bearish-side chart structure with marked levels; frame 3630 shows an account table containing multiple XAUUSD sell positions with explicit entry/SL/TP fields.

This directly confirms that bearish/sell-side execution is demonstrated in the primary artifact. It does not uniquely establish the mathematical mirror of the bullish executable rules. Bearish swing selection, LH/high selection, Entry activation, SL boundary, trigger taxonomy, AB=CD anchor transformation, and bearish 2X execution semantics remain unresolved.

## Cross-fixture evidence boundary

The combined primary artifact supports the conceptual chain:

`Spike → 2 Leg → AB=CD concept → Entry/SL/targets → bullish + bearish worked examples`

Conceptual confirmation is not deterministic executable geometry. The following remain explicitly non-canonical:

- exact swing-selection algorithm;
- exact Entry activation timestamp/price semantics;
- exact Leg-2 start semantics;
- exact SL boundary/buffer;
- pending-order replacement/refresh/expiry/invalidation state machine;
- exact 1/2/3-candle trigger taxonomy;
- complete 2X activation/order/fill/sizing semantics;
- A/B/C/D AB=CD anchors and tolerance;
- exact bearish mirror geometry;
- P-Gap numeric formula;
- any account-table TP/SL ratio interpreted as canonical R semantics.

## Gate decision

**Source Resolution: PARTIAL PASS — strengthened by primary-artifact, worked-example, and F14/F15 micro-forensic evidence.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production implementation was changed.
