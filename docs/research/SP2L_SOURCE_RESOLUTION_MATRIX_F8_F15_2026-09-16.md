# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE + WORKED-EXAMPLE EVIDENCE / REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER + WORKED-EXAMPLE EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + WORKED-EXAMPLE 2X EVIDENCE / EXACT EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT CONFIRMED AB=CD CONCEPT + WORKED-EXAMPLE EVIDENCE / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT + WORKED-EXAMPLE DIRECTIONAL EVIDENCE / EXACT EXECUTION GEOMETRY UNRESOLVED** | No | BLOCKED |

## Worked-example forensic update

Batch 19 reconstructed the clearest worked material without promoting inferred formulas. The main bearish execution episode visibly contains multiple sell entries, different SL values, shared TP values for several positions, a pending `sell limit` row, and chart annotations including `2x`, `E`, and numbered levels. A separate bullish teaching view visibly marks local lows/levels and `EMA 60 / M1`.

The worked material strengthens the existence of these concepts but does not uniquely identify the executable mapping from chart structure to order prices. In particular, the account tables cannot uniquely determine A/B/C/D anchors, exact Entry activation, exact SL boundary, pending-order lifecycle, trigger taxonomy, or the 2X formula. Direct arithmetic checks are recorded in `SP2L_BATCH19_WORKED_TRADE_RECONSTRUCTION_F8_F15_2026-09-16.md` and are explicitly observational, not canonical.

## Gate decision

**Source Resolution: PARTIAL PASS — strengthened by primary-artifact and worked-example evidence.**

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
- exact 2X formula, activation/order/fill/sizing semantics;
- A/B/C/D AB=CD anchors and tolerance;
- exact bearish mirror geometry;
- any assumption that bullish/bearish symmetry resolves lower-level geometry;
- any assumption that account-table TP/SL ratios define canonical R semantics.

No backtest variant was selected from this evidence and no production implementation was changed.

## Next research target

Continue dense timestamped inspection of the primary artifact around the first order-placement event, the visible `delete` action, and the 2X/risk diagram. The target is explicit spoken or graphical evidence that uniquely closes one blocker. If the artifact still does not uniquely resolve a semantic, it remains unresolved.
