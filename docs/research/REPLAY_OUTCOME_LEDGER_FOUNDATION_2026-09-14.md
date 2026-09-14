# Replay + Outcome Ledger Foundation — 2026-09-14

## Purpose

The implementation is moving forward independently of unresolved source geometry.
This layer answers **how validated signals are replayed and measured**, not **what
constitutes a Strategy A setup**.

## Components

### TradeLedger

`src/replay/trade-ledger.ts` provides deterministic accounting for:

- signal identity;
- direction and prices;
- risk in price units;
- expected R;
- OPEN/WON/LOST/CANCELLED lifecycle;
- exit timestamp/price;
- realized R.

It deliberately has no setup-detection logic and no inferred entry/stop/target
rules.

### Invariants

- duplicate trade IDs are rejected;
- unknown trade IDs are rejected;
- non-positive risk is rejected;
- TARGET and STOP outcomes require an exit price;
- CANCELLED trades have no realized R;
- realized R is derived from direction, entry, exit, and risk only.

## Gate policy

This is infrastructure, not a source-closure attempt. No unresolved geometry is
promoted and no historical performance is used to interpret source meaning.

The next implementation step is a replay adapter that consumes the repository's
versioned OHLC dataset and feeds candles into the deterministic engine. It will
remain execution-neutral until a complete canonical entry/SL/TP specification
exists.
