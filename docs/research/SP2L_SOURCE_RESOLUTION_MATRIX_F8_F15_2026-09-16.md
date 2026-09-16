# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction and micro-forensic inspection of order/2X/risk diagrams. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE + WORKED-EXAMPLE EVIDENCE / REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER + WORKED-EXAMPLE EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + PRIMARY GEOMETRIC MIDPOINT EVIDENCE / EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT CONFIRMED AB=CD CONCEPT + WORKED-EXAMPLE EVIDENCE / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT + WORKED-EXAMPLE DIRECTIONAL EVIDENCE / EXACT EXECUTION GEOMETRY UNRESOLVED** | No | BLOCKED |

## Micro-forensic update — order / 2X / risk diagrams

Batch 20 inspected the dense sequence around approximately 39:00–44:00 of the primary artifact.

### F11 — pending order lifecycle

Frames around 2340–2460 seconds visibly teach a horizontal `Buy Limit` level and contain a handwritten `delete` annotation in the same instructional sequence. This is direct evidence for pending-order placement and deletion as taught actions. The artifact still does not uniquely identify the state-transition condition: cancellation, replacement, invalidation, expiry, or another management action cannot be distinguished without inference.

### F13 — 2X geometric relation

The dedicated primary diagram around 2520 seconds explicitly labels `Buy`, `2X`, and `SL`. The drawn distance markers depict the `2X` level midway between Buy and SL, with the two segments shown as equal divisions of the Buy→SL span. This is stronger primary evidence than a chart-only annotation and supports the source-level geometric relation that 2X is at the midpoint of the Buy→SL distance.

This does **not** close the complete execution rule. The artifact does not uniquely specify whether Buy denotes intended entry, filled entry, or order level in every context; nor does it uniquely specify 2X order type, activation trigger, fill semantics, sizing, or cancellation/replacement interaction.

Therefore: **the geometric 50%-relation is primary-artifact-supported; complete 2X execution semantics remain unresolved.**

### F9 / F10 — Entry, TP1, TP2, SL separation

The dedicated diagram around 2550 seconds explicitly labels four distinct levels: `TP2`, `TP1`, `Entry`, and `SL`. This directly supports the distinction among these levels. It does not uniquely define how Entry, TP1, TP2, or SL are calculated from candle structure or AB=CD anchors, nor does it establish the exact activation/fill semantics.

### Round-level evidence

A later diagram around 2640 seconds contains handwritten `Round level` annotations and example price levels. This confirms that round levels are part of the taught material, but the deterministic round-level algorithm remains unresolved and is outside the F8–F15 closure set.

## Gate decision

**Source Resolution: PARTIAL PASS — strengthened by primary-artifact, worked-example, and micro-forensic evidence.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

## Explicit non-canonical items preserved

- exact swing-selection algorithm;
- exact Entry activation timestamp/price semantics;
- exact Leg-2 start semantics;
- exact SL boundary/buffer;
- pending-order replacement/refresh/expiry/invalidation state machine;
- exact 1/2/3-candle trigger taxonomy;
- complete 2X activation/order/fill/sizing semantics (while the midpoint geometry is primary-artifact-supported);
- A/B/C/D AB=CD anchors and tolerance;
- exact bearish mirror geometry;
- any assumption that bullish/bearish symmetry resolves lower-level geometry;
- any assumption that account-table TP/SL ratios define canonical R semantics.

No backtest variant was selected from this evidence and no production implementation was changed.
