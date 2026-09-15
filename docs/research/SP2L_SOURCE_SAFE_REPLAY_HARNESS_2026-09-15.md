# SP2L Source-Safe Replay Harness — 2026-09-15

## Purpose

Provide deterministic replay plumbing for source-safe synthetic fixtures after
source resolution has stopped, without promoting unresolved Strategy A
geometry into executable logic.

## Contract

The harness consumes `SyntheticFixture` objects and emits an ordered sequence
of observation events. Each event preserves:

- fixture identifier;
- candle index and timestamp;
- bullish/bearish direction as fixture metadata;
- source provenance references;
- the complete current geometry-status inventory.

A final `geometry_blocked` event makes the research gate explicit.

## Explicit non-goals

This harness does **not** define or infer:

- P-Gap candle pairs, OHLC boundaries, or indices;
- entry price anchors or fill semantics;
- Leg-2 start geometry;
- structural invalidation wick/body/close boundaries;
- pending-order refresh thresholds;
- 1/2/3-candle trigger acceptance rules;
- AB=CD anchors or tolerance;
- TP1/TP2/2X formulas;
- bullish/bearish executable mirror rules;
- buffers or optimization-selected constants;
- BUY/SELL decisions or production execution.

## Determinism requirements

1. Input fixtures must pass the source-safe fixture validation contract.
2. Candle observations are emitted in fixture candle-index order.
3. Event sequence numbers are contiguous from zero.
4. Source references are copied to every event; provenance is never discarded.
5. Missing labels for any blocked executable dimension cause replay rejection.
6. `execution_authorized` is permanently false in this layer.

## Research interpretation

The replay result is an evidence/research timeline, not a strategy signal
timeline. A future source discriminator may update a fixture's evidence label,
but replay infrastructure must not convert that label into a trading action.
Canonical geometry can only enter through the separate source-resolution and
manual-adjudication gates.

## Current gate

**SOURCE-SAFE REPLAY READY — EXECUTION BLOCKED.**

This artifact does not advance the project to Frozen Geometry. It only makes
future source evidence replayable without silently filling unresolved gaps.
