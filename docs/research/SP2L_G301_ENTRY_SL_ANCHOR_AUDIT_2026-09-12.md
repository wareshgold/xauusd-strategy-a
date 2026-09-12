# SP2L G301 — Entry / Structural SL Anchor Audit

**Date:** 2026-09-12  
**Status:** `SOURCE_CONFIRMED_MECHANISM__PRICE_ANCHORS_UNRESOLVED`

## Entry

Source evidence confirms pending-limit order placement. The exact executable price anchor is not uniquely established by the reviewed source sequence.

The current research implementation is materially different: `detectEntryTrigger()` waits for the first post-correction candle whose close reclaims the correction extreme and sets that close as `entryPrice`. fileciteturn624file0L2-L6

### Entry decision

- Pending-limit mechanism: `SOURCE-CONFIRMED`
- Exact price anchor: `UNRESOLVED`
- Fill semantics: `UNRESOLVED`
- Entry=C: `NOT CONFIRMED`
- Entry=correction extreme: `NOT CONFIRMED`
- Entry=E/2x: `NOT CONFIRMED`
- Close-reclaim entry: `RESEARCH-HYPOTHESIS`, not canonical

## Structural Stop

Source evidence says the stop is placed behind the candle from which the Spike originated. The exact OHLC boundary is not frozen.

Current research invalidation instead uses the correction extreme and a close-based breach. Therefore both the location and execution semantics diverge from the source semantic.

### Stop decision

- Structural stop behind Spike-origin candle: `SOURCE-CONFIRMED SEMANTIC`
- Exact Low/High/body boundary: `UNRESOLVED`
- Buffer/spread adjustment: `UNRESOLVED`
- Intrabar/touch/close semantics: `UNRESOLVED`
- Current correction-extreme stop: `RESEARCH-HYPOTHESIS`, not canonical

## Freeze rule

Do not change production code to any candidate anchor based solely on backtest performance. A source example with an executable numeric Entry and SL, or an explicit source statement defining the price boundary, is required before freezing.

## Gate

`ENTRY_GEOMETRY = BLOCKED`

`SL_GEOMETRY = BLOCKED`

`CANONICAL_IMPLEMENTATION_CHANGE = NOT_AUTHORIZED`
