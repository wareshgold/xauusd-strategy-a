# SP2L G305 — Official Source Textual Reconciliation

**Date:** 2026-09-12  
**Status:** `OFFICIAL_TEXT_CONFIRMS_CORE_SEMANTICS__TARGET_EXECUTION_CONFLICT_REMAINS`

## Purpose

Cross-check the raw-video reconstruction against the creator's official SP2L page, using the official page only as authoritative textual evidence and not using third-party indicator implementations to fill gaps.

## Official-source confirmations

The official creator page confirms:

- SP2L is built around Spike → correction → continuation.
- A valid Spike is associated with a P-Gap; a sharp move without a gap is not valid.
- Bullish correction reaches the low of the previous candle; bearish correction reaches the high of the previous candle.
- A secondary entry may be placed at 50% of the Entry-to-SL distance.
- SL is placed behind the candle from which the Spike originated.
- The default TP stated on the page is 1:1 risk-to-reward.

Source: official creator page: https://poursamadi.com/sp2l-strategy/

## Important conflict with the video target-construction sequence

The raw video reconstruction previously documented a target-construction sequence containing TP1/TP2, Round Level and Point Distance annotations (250/500/1000). The official page's textual summary states a default TP of 1:1.

These statements cannot be silently collapsed into one executable formula. The correct interpretation is:

1. `TP default = 1:1` is official textual evidence.
2. `TP1/TP2 + Point Distance + Round Level` are source-visual concepts from the primary video.
3. The relationship between these concepts is unresolved.
4. The official page does not establish that TP2=2R, that 250/500 map directly to TP1/TP2, or that Round Level selects the terminal target.
5. The page also does not provide the exact pending-limit price anchor or exact structural SL OHLC boundary.

## Source priority decision

No third-party indicator implementation is permitted to override or complete this conflict. Third-party pages may be retained as non-authoritative research leads only.

## Gate impact

`SOURCE_SEMANTICS = STRENGTHENED`

`TARGET_FORMULA = UNRESOLVED`

`ENTRY_ANCHOR = UNRESOLVED`

`SL_ANCHOR = SEMANTICALLY_CONFIRMED / PRICE_BOUNDARY_UNRESOLVED`

`FROZEN_GEOMETRY = BLOCKED`

No implementation changes are authorized.
