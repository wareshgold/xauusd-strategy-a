# SP2L G257 — Pending-Limit Visual Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `PENDING_LIMIT_SEMANTIC_CONFIRMED__PRICE_ANCHOR_UNRESOLVED`

## Source pass

Frame-by-frame review of the source construction around 38:00–39:45 was performed after the AB=CD pass. The teacher explicitly marks a `Buy Limit` on the bullish schematic and separately illustrates the structural SL region. The sequence shows that the entry is intended as a pending limit order rather than a market close-reclaim substitution.

The earlier source statement that a bullish correction reaches the low of the previous candle remains consistent with the visual construction. However, the exact price coordinate used for the pending Buy Limit is not uniquely recoverable from the schematic alone: the horizontal order line can be related to the surrounding candle structure, but the source does not label it with an unambiguous OHLC field or numerical price.

## Candidate mappings still prohibited from freeze

- Buy Limit = correction candle low.
- Buy Limit = previous candle low.
- Buy Limit = geometric C.
- Buy Limit = E measurement label.
- Buy Limit = 2x midpoint.
- Buy Limit = any fixed percentage of the spike.

The source's secondary-entry concept at 50% of Entry-to-SL is separate and must not be silently promoted to the primary entry formula.

## Decision

The pending-limit execution mechanism is source-confirmed. The executable entry price remains unresolved. Production code must not substitute a market order or invent a price anchor.

### Gates

- SOURCE RESOLUTION: `PASS_PARTIAL`
- B2 correction semantic: `FROZEN`
- Pending-limit mechanism: `FROZEN`
- Entry price geometry: `BLOCKED`
- FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`
- DEV: `BLOCKED`
- VALIDATION: `PROTECTED`
- PRODUCTION: `BLOCKED`
