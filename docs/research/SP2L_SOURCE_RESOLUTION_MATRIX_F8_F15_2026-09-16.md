# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE EVIDENCE / REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT / 50%-DISTANCE VISUAL SUPPORT / EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT CONFIRMED AB=CD CONCEPT / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT DIRECTIONAL EVIDENCE / EXACT EXECUTION GEOMETRY UNRESOLVED** | No | BLOCKED |

## Primary-artifact forensic evidence

### F8

Around 26:00–29:00 (approximately 1560–1740 s), the training material repeatedly illustrates bullish candle sequences and marks lower points/levels on candles. This strengthens the evidence that local candle lows/levels participate in the taught bullish structure. It does not uniquely specify the deterministic selection of the first important swing versus an evolving/latest swing when multiple candidates exist.

### F9

Around 39:30–41:00 (approximately 2370–2460 s), the artifact shows a horizontal `Buy Limit` level. Around 42:00–43:20 (approximately 2520–2600 s), a dedicated diagram separately labels `Buy`, `2X`, `TP1`, `TP2`, `Entry`, and `SL`. This directly supports distinct order/entry and risk/target levels. It does not establish an exact candle timestamp, touch/break/close activation rule, or `Entry = C` mapping.

### F10

The dedicated risk diagram around 42:00–43:20 explicitly labels `Entry` and `SL` as separate levels, with SL drawn below the bullish setup. The artifact therefore confirms a distinct SL level in the taught example, but does not establish wick/body/open/close/structural-swing boundary, buffer, or invalidation timing.

### F11

Around 39:30–41:00 the artifact demonstrates `Buy Limit` placement. Around 40:30–41:00 it also contains a visible `delete` annotation while discussing order/money handling. This is direct primary-artifact evidence that pending-order placement and deletion are taught. It does not uniquely specify when an older order must be deleted, replaced by a newer level, expired, invalidated, or allowed to coexist with another order.

### F12

Around 36:00–38:00 (approximately 2160–2280 s), the training material combines the SP2L diagram with `AB=CD` and `Valid BO = P-Gap`. Around 39:30–41:00 it demonstrates order placement at a horizontal `Buy Limit` level. This strengthens the breakout/validation and order-placement concept, but does not uniquely resolve a canonical 1-, 2-, or 3-candle trigger family or touch/break/close/retest timing.

### F13

Direct inspection confirms `2X` is explicitly taught. Around 42:00–42:35, the diagram labels `Buy`, `2X`, and `SL` on three horizontal levels with distance markers; the 2X level is visually between Buy/Entry and SL, consistent with the previously documented 50%-distance concept. Around 42:40–43:20, the sequence labels `TP1`, `TP2`, `Entry`, and `SL`. Exact activation, order type, fill, replacement/cancellation, sizing, and interaction with an existing Entry remain unresolved.

### F14

Around 37:00–37:25 the training slide explicitly displays `AB=CD` above the SP2L diagram. This directly confirms the AB=CD/equal-leg concept in the primary artifact. The reviewed frames do not uniquely define A/B/C/D anchors, wick/body semantics, projected versus observed D, equality/ratio interpretation, numeric tolerance, or the candle-selection algorithm.

### F15

The primary artifact contains both bullish and bearish SP2L teaching material and presents the setup directionally. This supports a bearish counterpart concept, but the reviewed material does not uniquely establish that every lower-level execution detail is a strict mathematical mirror, including exact LH selection, High semantics, trigger path, pending-order handling, and SL boundary.

## Gate decision

**Source Resolution: PARTIAL PASS — strengthened by primary-artifact evidence.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

## Explicit non-canonical items preserved

- exact swing-selection algorithm;
- exact Entry activation timestamp/price semantics;
- exact SL boundary/buffer;
- pending-order replacement/refresh/expiry state machine;
- exact 1/2/3-candle trigger taxonomy;
- exact 2X activation/order/fill semantics;
- A/B/C/D AB=CD anchors and tolerance;
- exact bearish mirror geometry;
- any assumption that bullish/bearish symmetry resolves lower-level geometry.

No backtest variant was selected from this evidence and no production implementation was changed.

## Next research target

Continue dense timestamped inspection of the same primary artifact, prioritizing the worked trade examples and the order-placement / 2X sections where the presenter may visually disclose exact anchor, invalidation, replacement, and trigger semantics. If the artifact still does not uniquely resolve those semantics, they remain unresolved.
