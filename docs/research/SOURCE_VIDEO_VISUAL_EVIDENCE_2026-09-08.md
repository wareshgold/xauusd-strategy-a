# Source Video Visual Evidence — 2026-09-08

**Status:** Research evidence only — no production Strategy A changes
**Branch:** `research/source-video-visual-evidence-2026-09-08`
**Parent:** `3385b39a135bc93940515168982fac38fba2d327`

## Supplied source material

A user-supplied video excerpt was inspected frame-by-frame:

- YouTube source supplied in chat: `https://youtu.be/7HEC5mO3d3U?si=ipD3BhS6MWsYntdq`
- Uploaded excerpt filename: `پورصمدی منقطع.mp4`
- Duration: ~259.33 s (4:19)
- Video SHA-256: `a445c70d4bd950060491e02f95b44fa54d77ef0eb65a43f20a5eb2e188649d72`

The uploaded file is treated as the visual evidence actually inspected. No claim is made here that every later chart frame is original teacher/source material; the excerpt transitions from a teaching slide/diagram into trading-platform/chart material.

## Direct visual observations

### 1. Explicit `AB = CD` equality is visibly written

In the opening teaching/diagram section (approximately 0–35 s), the frame visibly contains the handwritten statement:

> `AB = CD`

This is direct visual evidence that the source teaches an equality relationship between the two legs. This materially strengthens the existing G6 source evidence.

**Interpretation allowed by this evidence:**

- The source-supported relationship is exact-looking leg equality: `|AB| = |CD|` in the demonstrated construction.
- This is evidence for the qualitative G6 relationship already recorded in the Knowledge Map.
- It does **not** by itself establish a numerical tolerance for historical/simulator implementation. No tolerance is invented here.

### 2. The teaching slide also visibly references `1M` and `5M`

The same opening sequence contains handwritten `1M` and `5M` annotations adjacent to the SP2L diagram.

Record this as source-visible timeframe context only. Do not infer a mandatory timeframe rule from the excerpt without the corresponding spoken/source context.

### 3. The teaching slide visibly labels a breakout condition `Valid BO = P-Gap`

The opening diagram visibly contains the printed text:

`Valid BO = P-Gap`

This should be preserved as literal source evidence. The abbreviated `P-Gap` wording is not expanded or mathematically redefined here because the excerpt alone does not establish the exact intended expansion.

### 4. The diagram visually shows a multi-swing spike → correction → second-leg construction

The handwritten diagram in the opening section is consistent with a sequence containing an initial directional move, an intervening correction, and a subsequent directional leg. This supports the existing source semantics that SP2L is a two-leg construction rather than a single-candle measurement.

However, the excerpt does **not** expose sufficiently unambiguous labeled A/B/C/D price coordinates to freeze the exact G4 Leg-1 endpoint family or G5 C-origin candidate.

## What this resolves vs. what remains blocked

| Gate | Result from this video excerpt | Action |
|---|---|---|
| G6 — Leg2 ≈ Leg1 | **SOURCE-SUPPORTED; stronger direct evidence: `AB = CD` is visibly written** | Preserve exact equality as source evidence; tolerance remains TBD |
| G4 — Leg1 endpoints | **NOT RESOLVED** | Do not choose among structural low/high, breakout→extreme, spike-start→end, candle-open→extreme, or teacher-point alternatives without labeled source coordinates |
| G5 — Leg2 origin C | **NOT RESOLVED** | Do not equate C with pending limit/fill; exact visual C remains unresolved from this excerpt |
| G7 — lifecycle | **PARTIALLY SUPPORTED** | Sequence is visually consistent with correction before second leg, but simulator execution semantics remain separate |

## Important distinction: source teaching vs. later chart material

Around the 50 s mark the excerpt transitions to a MetaTrader-style chart/order-history view. Those later frames contain platform annotations such as `E`, `2x`, order rows, red zones and executed prices.

Those platform observations must not be promoted to source semantics merely because they appear in the supplied video. In particular:

- order/fill price is not automatically geometric C;
- red rectangles are not automatically canonical geometry;
- platform execution behavior is not automatically the teacher's geometric definition;
- historical chart measurements must not be used to reverse-engineer source meaning.

This preserves the repo's source-first hierarchy.

## Consequence for Phase 38 / G4-G5 work

The new evidence is strong enough to update the evidence ledger for **G6**, but it is deliberately insufficient to freeze G4 or G5.

The correct next source-resolution action remains visual extraction of labeled source coordinates from frames where the teacher explicitly identifies the endpoints/origin. The existing Phase 38 machinery can then test the extracted points against all candidate families without guessing.

## Guardrails

- No production Strategy A code changed.
- No canonical G4/G5 candidate selected.
- No historical optimization performed.
- No equality tolerance, ATR buffer, tick buffer, percentage threshold, or candle-count rule introduced.
- Fresh Holdout remains locked.

## Provenance note

This document records observations from the user-supplied video excerpt available in the conversation on 2026-09-08. It is an evidence registration artifact, not a replacement for the original source media or a claim that the excerpt contains every source frame needed for canonical SP2L resolution.
