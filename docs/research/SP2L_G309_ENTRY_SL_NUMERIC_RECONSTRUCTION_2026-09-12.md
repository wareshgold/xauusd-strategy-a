# SP2L G309 — Entry / SL Numeric Reconstruction

**Date:** 2026-09-12
**Status:** `SEMANTIC_SOURCE_ALIGNMENT__NUMERIC_PRICE_ANCHORS_UNRESOLVED`

## Source evidence

The direct video review confirms a bullish construction with Buy, `2x`, and SL annotations, followed by the clean TP1/TP2/Entry/SL schematic.

The earlier worked order-panel examples remain important cross-checks:
- Example A: Entry 3229.08, SL 3237.12, TP 3213.44.
- Example B: Entry 3223.84, SL approximately 3235.50, TP 3213.33.
- Example C: Entry 3228.88, SL approximately 3235.50, terminal TP around 3213.45 when shown.

The different Entries with approximately clustered target prices reject a universal `TP = final Entry ± 2R` assumption.

## Entry

Pending-limit entry is source-supported, but the exact price level is not uniquely identified by the reviewed frames.

Do not infer:
- Entry = C;
- Entry = correction extreme;
- Entry = E label;
- Entry = 2x;
- Entry = fill price of a geometric C point.

## SL

The source semantic is a structural stop behind the candle from which the Spike originated. The reviewed schematic does not establish whether the executable boundary is the wick extreme, body edge, another OHLC reference, or includes a buffer.

## Decision

`ENTRY_PRICE = UNRESOLVED`
`SL_PRICE = UNRESOLVED`
`FILL_SEMANTICS = UNRESOLVED`
`STOP_TRIGGER_SEMANTICS = UNRESOLVED`
`CANONICAL_ORDER_GEOMETRY = BLOCKED`
