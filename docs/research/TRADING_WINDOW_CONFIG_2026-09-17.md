# SP2L Strategy A — Trading Window Configuration

**Date:** 2026-09-17
**Status:** Research configuration — NOT a frozen production rule
**Scope:** Trading-time eligibility only

## Purpose

Strategy A research and eventual execution must permit trades only inside a configurable London-to-New-York trading window.

This configuration is intentionally separated from SP2L geometry. Changing the window later must not require redefining Spike, Leg 1, Leg 2, P-Gap, AB=CD, entry, or risk semantics.

## Canonical time representation

- Historical stored timestamps: UTC.
- London session timezone: `Europe/London`.
- New York session timezone: `America/New_York`.
- DST handling: IANA timezone rules.
- Local/Iran display time is not the canonical session-definition basis.

## Current window definition

```text
window_start = London Open
window_end   = New York Session End
```

The exact clock values are configuration parameters and are intentionally NOT frozen by this document.

### Configuration contract

```yaml
trading_window:
  start:
    market: london
    timezone: Europe/London
    event: open
    clock: configurable
  end:
    market: new_york
    timezone: America/New_York
    event: session_end
    clock: configurable
```

## Semantics

A candidate trade is time-eligible only when its canonical UTC timestamp, converted through the relevant IANA timezone rules, lies within the configured London-open through New-York-end interval.

The window is a research/execution constraint. It does not define or modify SP2L geometry.

## Explicit non-goals

This document does NOT:

- define exact London or New York clock hours;
- infer hours from broker gaps;
- infer hours from backtest performance;
- define entry/exit/fill semantics;
- define SP2L geometry;
- change production BUY/SELL logic;
- authorize live trading.

## Change policy

If the research later changes the trading window, only this configuration and the associated validation evidence need to be versioned and revalidated. SP2L geometry remains unchanged unless independently resolved by source evidence.

## Gate status

- Trading-window concept: RESOLVED
- Timezone basis: RESOLVED
- Exact clock endpoints: CONFIGURABLE / NOT FROZEN
- Geometry freeze: BLOCKED by independent source-resolution items
- DEV/VAL/Fresh Holdout: unchanged and locked
- Production: OFF
