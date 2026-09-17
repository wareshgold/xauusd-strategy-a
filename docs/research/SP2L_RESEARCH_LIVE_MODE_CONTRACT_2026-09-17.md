# SP2L Research Live Mode Contract — 2026-09-17

## Purpose

Define a deterministic, research-only live-observation boundary for future MT5 integration without defining or promoting canonical Strategy A signal semantics.

## Contract

A future live adapter may provide normalized closed-bar observations with:

- provider/server identity;
- symbol identity;
- timeframe;
- UTC bar timestamp;
- OHLC(V) values;
- monotonic observation sequence where available;
- source/retrieval metadata.

The adapter must not silently alter prices, timestamps, missing bars, or symbol identity.

## Closed-bar rule

The research observer consumes only completed bars. In-progress bars must not be treated as confirmed observations.

## Duplicate/idempotency rule

Repeated delivery of the same provider bar identity must be idempotent. A duplicate observation must not create a second research event.

## Gap rule

Missing or discontinuous bars are recorded as data-quality events. The observer must not invent candles to repair gaps.

## Signal boundary

Until Frozen Geometry and all required source/execution semantics are resolved, the live observer may emit only non-canonical events such as:

`OBSERVATION`
`DATA_QUALITY_EVENT`
`RESEARCH_DIAGNOSTIC`

It must not emit production `BUY` or `SELL` events.

## Telegram boundary

A future Telegram adapter is a notification transport only. It must receive an already-authorized event and must not calculate SP2L geometry, alter direction, or independently create a trade signal.

For research mode, Telegram output must be explicitly labelled as research/observation and must not imply production authorization.

## MT5 boundary

An MT5 adapter is responsible only for provider/terminal communication and normalized market observations unless a separate, explicitly authorized execution adapter is introduced later.

The existence of MT5 execution-domain code in the repository does not authorize live order placement.

## Promotion gate

This contract does not resolve:

- P-Gap formula;
- spike definition beyond currently source-confirmed material;
- AB=CD anchors/tolerance;
- entry/fill semantics;
- SL/invalidation semantics;
- TP2 geometry;
- Round Level geometry;
- canonical lifecycle;
- production BUY/SELL rules.

Those remain source-resolution and validation gates.

## Test intent

Synthetic fixtures should cover:

1. one completed bar -> one observation;
2. duplicate completed bar -> no duplicate event;
3. out-of-order bar -> deterministic handling;
4. timestamp normalization;
5. missing bar -> data-quality event, no fabricated candle;
6. in-progress bar -> ignored;
7. research event -> Telegram transport receives research label only;
8. no code path from research observer directly to production order execution.
