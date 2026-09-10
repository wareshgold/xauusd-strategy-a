# SP2L G259 — Structural SL Anchor Cross-Reference

**Date:** 2026-09-10
**Gate:** SOURCE RESOLUTION
**Status:** `SEMANTIC_CONFIRMED__OHLC_BOUNDARY_UNRESOLVED`

## Evidence

The source explicitly teaches SL placement behind the candle from which the Spike originated. The walkthrough visual sequence around 38:35–39:40 shows a structural SL line below the bullish originating structure while the Buy Limit is shown separately. The drawing therefore supports a structural stop tied to the Spike-origin candle rather than an arbitrary fixed-distance stop.

## What can be frozen

- SL is structural and associated with the Spike-origin candle: **FROZEN SEMANTICALLY**.
- SL is distinct from the Entry/Buy Limit level: **FROZEN**.
- A fixed numeric stop distance is not source-confirmed: **REJECTED AS CANONICAL**.

## What remains unresolved

- exact origin-candle index in multi-candle cases;
- wick extreme versus body boundary;
- exact price coordinate;
- buffer beyond the structural point;
- equality/touch semantics;
- intrabar versus close invalidation;
- spread/bid-ask handling;
- stop modification rules.

Do not freeze bullish `Low[origin]`, bearish `High[origin]`, a body boundary, or a numeric buffer merely by symmetry.

## Gate decision

SOURCE RESOLUTION: `PASS_PARTIAL`

B3 structural SL semantic: `FROZEN`

B3 executable OHLC boundary: `BLOCKED`

FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`

DEV / VALIDATION / FRESH HOLDOUT / PRODUCTION: unchanged and protected.

## Research fixture requirements

Synthetic cases must separately distinguish wick/body, exact touch, buffer/no-buffer, alternate origin-candle choices, and intrabar/close invalidation without using historical performance to choose the interpretation.