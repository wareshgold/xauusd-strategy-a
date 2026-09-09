# Research Engine Infrastructure v1 — 2026-09-09

## Purpose

Build reusable, strategy-neutral infrastructure in parallel with source-resolution work. Nothing in this layer selects or interprets Strategy A geometry.

## Implemented

### Data layer
- Immutable `Candle` model with OHLC invariants.
- UTC normalization for timestamps.
- Duplicate, chronological-order, OHLC-integrity and gap diagnostics.
- Deterministic lower-timeframe → fixed bucket OHLC aggregation.
- Incomplete source buckets are not emitted.
- Dataset SHA-256 fingerprint includes provider, symbol, timeframe, timezone, source version and ordered OHLC/timestamps.

### Order/backtest layer
- Explicit MARKET/LIMIT/STOP order types.
- BUY/SELL sides and lifecycle states.
- Pending-limit fill semantics using candle high/low.
- Separate stop-loss and take-profit fields.
- Explicit intrabar conflict policy; default is conservative stop-first when both protective levels are touched by the same candle.
- No strategy pattern detector and no Strategy A order generation.

### Reporting layer
- Closed-trade count, win/loss rate.
- Expectancy/average/median R.
- Profit factor.
- Maximum drawdown in R.
- Maximum consecutive losses.
- Average holding time.
- Long/short slices.

### Verification

`research/engine/test_engine.py` covers:
- data-integrity failure detection;
- complete/incomplete aggregation behavior;
- pending LIMIT fill and intrabar stop-first behavior;
- R-based directional metrics;
- order-independent dataset fingerprints.

A GitHub Actions workflow runs these tests on changes to the research engine.

## Explicit non-decisions

This infrastructure does **not** define:

- P-Gap geometry;
- entry anchor;
- stop/invalidation OHLC anchor;
- trigger acceptance/timing;
- AB=CD anchors or tolerance;
- Leg 1 / Leg 2 projection formula;
- TP1/TP2 projection;
- session filter;
- Strategy A setup validity;
- risk percentage or broker contract specification.

Those remain blocked by the source-resolution register and must not be inferred from infrastructure behavior or backtest results.

## Gate status

- SOURCE RESOLUTION: partial/ongoing
- SYNTHETIC FIXTURES: ongoing/pass for tested hypotheses
- FROZEN GEOMETRY: **BLOCKED**
- DEV / VALIDATION / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: **LOCKED**

The engine can be tested with synthetic, already-resolved orders. Such tests are mechanics verification only and are not Strategy A performance claims.
