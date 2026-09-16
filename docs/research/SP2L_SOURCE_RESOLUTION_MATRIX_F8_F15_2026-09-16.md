# SP2L Source Resolution Matrix — F8–F16 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F16** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction and primary-artifact micro-forensic passes. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT PENDING-ENTRY CONCEPT CONFIRMED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **SOURCE-CONFIRMED ORIGIN/RISK-SEPARATION CONCEPT / EXACT PRICE AND INVALIDATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE CONCEPT CONFIRMED / DELETE CONDITION AND REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER CONCEPT CONFIRMED / EXACT TRIGGER TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + BETWEEN-LEVEL VISUAL RELATION / EXACT PRICE FORMULA AND EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT EXPLICIT AB=CD / CONCEPT CONFIRMED / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT BEARISH EXECUTION CONFIRMED / EXACT MIRROR GEOMETRY UNRESOLVED** | No | BLOCKED |
| F16 | Round level | **SOURCE-CONFIRMED CONCEPT / MULTIPLE SPACING CANDIDATES OBSERVED / EXACT ROUND-LEVEL ALGORITHM UNRESOLVED** | No | BLOCKED |

## Batch 27 — F9/F10/F11/F12 primary trigger/order forensic update

A dedicated frame-by-frame forensic pass inspected the primary sequence at approximately **38:00–41:00**.

Observed evidence:

- ~38:00: `Valid BO = P-Gap` is explicitly displayed.
- ~38:30: multiple local lower points are visibly marked.
- ~39:00–39:15: `BO` and `Buy Limit` are introduced in the same bullish teaching sequence.
- ~39:30–39:55: a horizontal level is explicitly labeled `Buy Limit` and remains associated with the sequence.
- ~40:00: the order line remains present as the diagram advances.
- ~40:05–40:20: handwritten `delete` appears in the order-management sequence.
- ~40:25–41:00: additional `money` and numbered management annotations appear, without a source-complete order state machine.

The pass strengthens the following source boundaries:

**F12:** trigger concept is confirmed, but the exact taxonomy remains unresolved. The artifact does not uniquely distinguish touch, wick break, close confirmation, following-bar confirmation, or a specific multi-candle rule.

**F9:** a pending Buy Limit concept is directly confirmed, but activation/fill semantics and exact Buy Limit price construction remain unresolved.

**F10:** the diagram supports separation of entry and risk/SL concepts, but exact price and invalidation semantics remain unresolved.

**F11:** Buy Limit placement and deletion are directly taught behaviors, but the deletion condition, replacement/refresh rule, expiry, and multiple-order precedence remain unresolved.

No canonical rule is promoted from this pass.

## Gate decision

**Source Resolution: PARTIAL PASS — individual concepts and their teaching sequence strengthened; executable chain remains unresolved.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production implementation was changed.
