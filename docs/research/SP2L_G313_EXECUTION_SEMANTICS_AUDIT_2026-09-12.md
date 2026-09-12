# SP2L G313 — Execution Semantics Audit

**Date:** 2026-09-12
**Status:** `ORDER_MECHANISM_CONFIRMED__FILL_AND_TRIGGER_SEMANTICS_UNRESOLVED`

## Source-confirmed mechanism

The source supports pending-limit order placement during the correction. This mechanism must not be replaced with a close-reclaim market entry.

## Unresolved execution semantics

The source evidence reviewed so far does not uniquely specify:

- whether a limit order fills on touch of the exact price;
- bid/ask side used for fill;
- spread treatment;
- slippage assumptions;
- intrabar ordering when SL and TP are both crossed;
- whether stop invalidation uses touch or close;
- cancellation timing;
- whether the pending order survives subsequent structural changes;
- rounding to instrument tick size.

## Current implementation boundary

The research implementation currently uses a close-reclaim trigger, which is not equivalent to the source-confirmed pending-limit mechanism. It must remain quarantined from canonical Strategy A until geometry is frozen.

## Decision

`PENDING_LIMIT = SOURCE-CONFIRMED`
`FILL_RULE = UNRESOLVED`
`STOP_EXECUTION = UNRESOLVED`
`TARGET_EXECUTION = UNRESOLVED`
`ROUNDING_SPREAD_SLIPPAGE = UNRESOLVED`
`CANONICAL_EXECUTION_ENGINE = BLOCKED`
