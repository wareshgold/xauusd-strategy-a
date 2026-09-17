# SP2L Source Resolution Matrix — F8–F16 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F16** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video plus author-associated source material. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **AUTHOR-ASSOCIATED SECOND-LEG TRIGGER + PRIMARY-ARTIFACT PENDING/EXECUTED STATES CONFIRMED / ACTIVATION & FILL SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **AUTHOR-ASSOCIATED ORIGIN-CANDLE SL CONCEPT + WORKED-TRADE INSTANCES OBSERVED / EXACT PRICE & INVALIDATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT TEMPORAL PERSISTENCE + DELETE + WORKED-TRADE HISTORY CLUSTERED / LIFECYCLE CAUSALITY UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **AUTHOR-ASSOCIATED P-GAP VALIDITY + SECOND-LEG TRIGGER CONCEPT + PRIMARY-ARTIFACT BO ORDERING CONFIRMED / EXACT EXECUTABLE TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **AUTHOR-ASSOCIATED 50%-OF-ENTRY-TO-SL SECONDARY-ENTRY RELATION CONFIRMED / FULL 2X ORDER, SIZING & LIFECYCLE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT EXPLICIT AB=CD / CONCEPT CONFIRMED / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **AUTHOR-ASSOCIATED UP/DOWN SECOND-LEG MIRROR + PRIMARY-ARTIFACT BEARISH EXECUTION CONFIRMED / EXACT MIRROR GEOMETRY UNRESOLVED** | No | BLOCKED |
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

## Batch 28 — temporal pending-order state reconstruction

A dense 5-second sequence from approximately **39:00–41:00** was reconstructed as a temporal ledger rather than as isolated frames.

Observed sequence:

`BO context → Buy Limit shown → pending level persists → delete annotation → newer reference becomes visible → money/management annotations`

At ~39:30–39:40, `Buy Limit` is explicitly associated with a horizontal level and a separate lower `SL` reference is added. At ~40:00 the horizontal level remains while the represented price is above it. Around ~40:05, `delete` is written while a newer blue/sloped reference appears near the newer price structure. This is consistent with a possible stale-order/candidate-refresh context, but the artifact does not explicitly state that the newer reference replaces the old pending order.

Therefore the source-aligned update is:

**F11 = temporal persistence + delete observed / replacement causality unresolved.**

The following remain non-canonical:

- delete = replacement;
- delete = invalidation;
- delete = timeout;
- delete = manual cancellation;
- newer reference = new pending order;
- any multiple-order precedence rule.

The same temporal sequence strengthens F12 only at the ordering level: `BO / valid-BO context` precedes the pending Buy Limit teaching and later management. It still does not prove wick-vs-close, touch-vs-break, next-candle confirmation, or a 1/2/3-candle taxonomy.

F9 remains pending-entry confirmed but activation/fill unresolved. F10 remains entry/risk separation observed but exact price/invalidation unresolved.

## Batch 29 — worked-trade execution/account forensic pass

A primary-artifact forensic pass inspected the worked-trade/account material across approximately **58:00–67:30**, with particular attention to the account tables around **59:00–60:30** and the worked-history tables around **65:00–67:30**.

Observed evidence:

- ~58:00–58:30: the chart is explicitly annotated `SP2L`, `EMA60`, and `M1`, providing contextual identification of the worked chart; these annotations do not by themselves define executable geometry.
- ~59:00–60:30: the account display contains multiple XAUUSD **sell** positions with distinct entry prices and SL/TP fields. This directly demonstrates an executed-position state in the teaching example, but does not disclose the exact event that caused each position to fill.
- ~59:30: visible position records include entries such as **3229.08 / SL 3237.73 / TP 3213.30**, **3223.84 / SL 3235.50 / TP 3213.37**, **3228.88 / SL 3235.50 / TP 3213.37**, and a **3232.41 / SL 3237.80 / TP 0.00** position. These are observations from the displayed account state, not canonical parameter definitions.
- ~65:00–66:30: the worked history shows completed sell positions with explicit entry/close prices and timestamps; several positions share the same TP **3213.37**, while other positions have no TP and later close at different prices.
- ~66:30: a separate history row around **3269.88** has no SL/TP and a later price around **3261.74** at `2025.05.12 04:14:28`. This demonstrates that a displayed order can exist without SL/TP in the worked account history, but it does not establish why or when that order was created, whether it was a pending order before execution, or whether it was managed manually.
- The account history also shows a pending-order-type row in the broader worked example, but the screenshots do not provide a source-complete mapping from that pending row to the exact chart event or to a deterministic fill condition.

Source-bound conclusions:

**F9:** executed positions are directly observed in the worked example, strengthening the distinction between an order/setup state and an executed-position state. The activation/fill event remains unresolved: the artifact does not prove touch, wick penetration, bar-close, next-bar confirmation, or another exact activation rule.

**F10:** entry and SL values are repeatedly displayed together in executed positions. This confirms that the worked example uses explicit SL values, but does not establish the canonical SL construction, invalidation boundary, or whether the displayed SL is always mechanically derived from the same source structure.

**F11:** the account/history material confirms that both pending-order and executed-position states can appear in the worked material. It does not provide enough temporal linkage to prove a deterministic pending → fill → management state machine, nor does it prove replacement, cancellation, expiry, or delete semantics.

**F13:** the worked example contains visible `2x` chart annotations and multi-position execution context, but the account tables do not expose a canonical 2X price formula, sizing rule, or fill semantics. The prior visual placement alone was not sufficient to promote 50%.

**Execution semantics:** account tables are evidence of observed platform state, not by themselves a canonical source for intrabar fill rules, spread/bid-ask handling, order priority, partial fills, slippage, or manual-vs-automatic execution.

No canonical rule is promoted from Batch 29.

## Batch 31 — worked-trade chart/history timeline forensic pass

A timeline-level reconstruction compared the visible chart context with the readable account/history records in the May 12 worked example.

Observed:

- The worked chart is explicitly identified as `SP2L`, `EMA60`, and `M1`.
- The chart and account screens share the same XAUUSD price region around 3213–3238.
- The account-position view contains the same entry/SL/TP values later visible in history, including 3229.08, 3223.84, 3228.88, and 3232.41.
- The history table contains a tight cluster at `2025.05.12 12:56:02` for the first three entries, all with close/current value `3213.37`.
- Later 3232.41 rows occur at `12:56:24`, `12:56:58`, and `12:57:06`, with displayed prices `3214.11`, `3214.72`, and `3215.80` respectively.
- A separate row around 3269.88 has no visible SL/TP and a later displayed price around 3261.74 at `2025.05.12 04:14:28`.

This is stronger temporal evidence than an isolated account screenshot, because the records can be ordered chronologically and the same prices recur across the worked account/history views.

However, the frames do **not** establish an event-level chart-to-history mapping. The evidence does not prove what the history `Time` column semantically represents, which exact candle caused each record, whether the three 12:56:02 rows were separate fills or another account action, whether the 3232.41 sequence represents repeated fills/closures/management, or whether any specific history row was preceded by the displayed Buy Limit. Automatic vs manual execution, touch/wick/close activation, bid/ask, slippage, partial-fill, and intrabar ordering semantics remain unresolved.

Therefore:

**F9 = pending + executed state + chronological history cluster confirmed / exact activation and fill semantics unresolved.**

**F11 = pending/executed account states + chronological records confirmed / pending→fill→management causality and lifecycle precedence unresolved.**

No canonical execution or lifecycle rule is promoted.

## Batch 35 — author-associated source resolution: P-Gap, second-leg trigger, SL, and 2X

A fresh source-resolution search located the author-associated SP2L page and exposed stronger indexed source text than the prior secondary evidence. The direct page fetch returned HTTP 403 during this pass, so the retrieval limitation is recorded; the search result itself is the source record used for this update.

The source states that a valid SP2L spike has a P-Gap between candles and that a sharp movement without a gap is not considered valid. It does not expose the numeric P-Gap formula, candle indexing, wick/body rule, minimum threshold, or tolerance.

The source states that after a spike correction, in an uptrend the corrective candle waits to reach the low of the previous candle; in a downtrend it waits to reach the high of the previous candle. Once the Second Leg is triggered, entry is taken in the spike direction. This strengthens F9/F12 at the concept level but does not specify touch/wick/close/broker activation semantics.

The source states that SL is placed behind the candle from which the spike originated. This confirms the origin-candle relationship but not the exact price boundary or invalidation event.

Most importantly, the source explicitly states that a secondary entry can be added at **50% of the distance from the entry point to the stop-loss**. This is now author-associated source evidence for the secondary-entry relation. It does not, by itself, resolve 2X sizing, whether the secondary entry is always used, exact pending-order behavior, or the full lifecycle.

Source-aligned resolution:

- **F9:** second-leg trigger concept strengthened; activation/fill semantics unresolved.
- **F10:** origin-candle SL concept strengthened; exact price/invalidation semantics unresolved.
- **F12:** P-Gap validity + second-leg trigger concept source-confirmed; exact executable taxonomy unresolved.
- **F13:** **50%-of-entry-to-SL secondary-entry relation source-confirmed; complete 2X execution/lifecycle semantics unresolved.**
- **F14:** unchanged; AB=CD concept confirmed, anchors/tolerance unresolved.

No canonical implementation is changed from this pass.

## Gate decision

**Source Resolution: PARTIAL PASS — materially strengthened by author-associated source evidence.**

**Frozen Geometry: BLOCKED** — executable semantics remain unresolved and cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production implementation was changed.
