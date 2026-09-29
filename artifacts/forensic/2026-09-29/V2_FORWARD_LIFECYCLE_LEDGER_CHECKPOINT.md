# V2 Forward Population/Lifecycle Ledger Checkpoint — 2026-09-29

## Status

**Research infrastructure added. Canonical Strategy A remains unchanged.**

Branch:
- `research/sp2l-legacy-mirror-backtest-20260929`

Latest commits:
- `eb47d48` — add deterministic V2 forward population lifecycle ledger
- `9659036` — add deterministic V2 forward ledger tests
- `a359a3f` — integrate V2 forward population lifecycle ledger
- `974b50f` — preserve V2 forward order rejection status

## Purpose

The Forward Test now persists a dedicated V2 lifecycle ledger alongside the
existing execution state. This is an attribution layer, not a new trading rule.

The ledger records:

```
DETECTED
  -> ORDER_PLACED
      -> FILLED
          -> CLOSED
      -> EXPIRED
  -> ORDER_REJECTED
  -> BLOCKED
  -> SUPPRESSED
```

Every record keeps the signal id, symbol, direction, trigger time, theoretical
entry, SL, TP, and risk. Broker order/deal identifiers and execution fields are
added as they become known.

## Important boundary

This patch **does not**:

- change V2 geometry;
- introduce a canonical lifecycle-overlap rule;
- infer fill semantics;
- infer intrabar SL/TP ordering;
- promote the 1360-trade lifecycle hypothesis;
- authorize production BUY/SELL decisions.

The ledger is deliberately observational so that Backtest/Forward population
differences can be attributed instead of silently discarded.

## Current forensic baseline

Verified exact historical signal population:

- MT5 bars: **87,673**
- historical signal population: **1,472**
- reference trade population: **1,356**
- current lifecycle hypothesis: **1,360**
- remaining trade-population gap: **4**
- reference outcomes: **836W / 520L**
- current lifecycle-hypothesis outcomes: **925W / 433L**

Therefore the outcome semantics remain unresolved.

## Next gate

1. Pull the branch.
2. Run the deterministic ledger tests.
3. Start the clean V2 XAUUSD forward runner in research/demo mode.
4. Verify that each detected signal receives a persistent ledger record.
5. Reconcile ledger records against MT5 order/deal lifecycle.
6. Only after that, investigate the remaining 4-trade population gap and the
   89-win / 87-loss outcome attribution difference.

No geometry changes are permitted in this phase.
