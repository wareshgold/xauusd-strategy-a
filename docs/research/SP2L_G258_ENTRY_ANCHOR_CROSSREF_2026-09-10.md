# SP2L G258 — Entry Anchor Cross-Reference

**Date:** 2026-09-10
**Gate:** SOURCE RESOLUTION
**Status:** `SEMANTIC_CONFIRMED__PRICE_ANCHOR_UNRESOLVED`

## Evidence

The source walkthrough repeatedly labels the intended order as `Buy Limit`. In the 38:40–39:40 visual sequence, the teacher draws a horizontal Buy Limit reference through the bullish construction and separately marks SL below the originating structure. The same sequence is consistent with a pending-limit entry rather than a market-close entry.

The visual evidence does **not** uniquely identify the exact OHLC coordinate of the Buy Limit line. Candidate interpretations include a prior-candle reference, correction reference, source measurement level, or another source-specific price. The annotation alone cannot distinguish them.

## Cross-reference result

- Pending-limit mechanism: **FROZEN**
- Entry direction follows Spike: **FROZEN**
- Exact Entry price anchor: **UNKNOWN**
- Entry = C: **NOT PROVEN**
- Entry = correction low/high: **NOT PROVEN**
- Entry = E: **NOT PROVEN**
- Entry = 2x: **NOT PROVEN**
- Fill price = geometric anchor: **NOT PROVEN**

## Important visual observation

The source drawing shows a horizontal Buy Limit level and a separate SL level, with a vertical distance annotation between them. This supports the existence of a measurable Entry-to-SL risk interval, but it does not establish which candle extreme generated Entry.

## Gate decision

SOURCE RESOLUTION: `PASS_PARTIAL`

B2 pending-limit mechanism: `FROZEN`

B2 executable Entry anchor: `BLOCKED`

FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`

DEV / VALIDATION / FRESH HOLDOUT / PRODUCTION: unchanged and protected.

## Rule

No deterministic Entry formula may be promoted until source evidence identifies the anchor unambiguously. Do not substitute a market entry for the pending Buy Limit.