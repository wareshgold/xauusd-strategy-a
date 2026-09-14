# Execution Simulator Foundation — 2026-09-14

## Purpose

Add execution infrastructure without promoting unresolved Strategy A execution semantics into canonical rules.

## Implemented

- Pending-order lifecycle.
- Explicit entry-touch fill rule as an injected configuration boundary.
- Stop/target touch detection from candle OHLC.
- TradeLedger integration.
- Explicit `AMBIGUOUS` outcome when one OHLC candle touches both stop and target.
- No inferred intrabar ordering.

## Source boundary

The simulator does **not** claim that `TOUCH_ENTRY` is the canonical Strategy A fill rule. It is an explicit simulator policy so tests can exercise the execution layer. Likewise, `OHLC_AMBIGUOUS` is a conservative data limitation, not a Strategy A rule.

Canonical promotion remains blocked until source evidence resolves pending-limit fill semantics and same-candle execution ordering where required.

## Why this advances the project

The replay stack can now represent:

`candidate → pending order → fill → open trade → target/stop/ambiguous`

without silently converting unresolved geometry into a profitable backtest assumption.

## Next

Build a generic metrics aggregator over closed TradeLedger records. It will report descriptive statistics only and will not optimize or select Strategy A parameters.
