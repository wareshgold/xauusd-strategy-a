# SP2L G300 — Worked Example Reconstruction Audit

**Date:** 2026-09-12  
**Status:** `SOURCE_RECONSTRUCTION__EXECUTABLE_BRIDGE_NOT_UNIQUELY_RESOLVED`

## Objective

Reconstruct one continuous source example from setup through order/target construction and determine whether the source provides a unique executable mapping for Spike origin, P-Gap, correction, Entry, SL, Leg 1/AB=CD, TP1/TP2, point distances, and Round Level.

## Source sequence reviewed

The primary SP2L video sequence previously extracted and audited covers approximately 39:40–44:40 of the target/order construction section.

Observed sequence:

- ~39:40: Buy/SL/order context appears.
- ~41:30: Buy / 2x / SL construction is shown.
- ~42:00–43:20: clean target schematic with Entry, SL, TP1 and TP2.
- ~43:40: `Round level 2` appears adjacent to the schematic.
- ~44:00: numerical examples including 2500, 3200, 3255 and 3250 appear.
- ~44:08–44:36: `250 point`, `500 point`, and later `1000` are written while the target schematic remains in context.

## Reconstruction findings

The source provides strong visual association between the target ladder and the concepts Round Level and Point Distance. However, the reviewed frames do not contain a unique arrow, equation, explicit label-to-price mapping, or complete spoken/text statement that assigns each numeric annotation to a particular executable target.

Therefore the following mappings remain **unresolved**:

- `250 point = TP1`
- `500 point = TP2`
- `1000 = Entry→TP2`
- `Round level 2 = terminal TP`
- `TP1 = 1R`
- `TP2 = 2R`
- `TP2 = AB=CD endpoint`
- exact A/B/C/D anchors
- exact Entry anchor
- exact structural SL OHLC boundary
- XAUUSD point/tick conversion
- rounding and spread treatment
- SELL mirror
- intrabar vs close execution

## Important cross-check

Earlier order-panel examples show materially different Entry/SL combinations with terminal TP values remaining approximately clustered around the same price. This is inconsistent with treating the terminal TP as a universal final-entry-based 2R formula. It does not by itself establish an alternative source formula.

The correct conclusion is **not** to select another formula; it is to keep target geometry unresolved until source evidence uniquely identifies it.

## Source-to-implementation boundary

The current Entry implementation is explicitly close-reclaim based: it waits for a post-correction candle close beyond the correction extreme and uses that close as `entryPrice`. This is not the source-confirmed pending-limit mechanism and must remain classified as a research hypothesis. fileciteturn624file0L2-L6

## Decision

`WORKED_EXAMPLE_BRIDGE = INSUFFICIENT_FOR_FREEZE`

`ENTRY_ANCHOR = UNRESOLVED`

`SL_ANCHOR = UNRESOLVED`

`ABCD_ANCHORS = UNRESOLVED`

`TP1_TP2_FORMULA = UNRESOLVED`

`ROUND_LEVEL_SELECTOR = UNRESOLVED`

`POINT_DISTANCE_MAPPING = UNRESOLVED`

`EXECUTION_SEMANTICS = UNRESOLVED`

No production or canonical implementation changes are authorized by G300.
