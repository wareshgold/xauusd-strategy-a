# Replay Harness Foundation — 2026-09-14

## Purpose

This implementation adds a deterministic candle-replay harness on top of the existing market-domain and execution-neutral deterministic engine.

## Data flow

```text
validated OHLC candles
        ↓
DeterministicEngine.push()
        ↓
EngineDecision
        ↓
ReplayRunResult
```

The harness counts candles, canonical signals, blocked decisions, and no-signal decisions while retaining the ordered decision stream.

## Deliberate boundary

The harness does **not** turn a pending-limit candidate into a filled trade. In particular it does not assume:

- that geometric C equals the fill price;
- when or whether a pending order fills;
- an exact structural stop boundary;
- TP1/TP2 or other target mapping;
- an AB=CD tolerance;
- any unresolved P-Gap geometry.

Those remain source-resolution/frozen-geometry dependencies.

Consequently this layer is suitable for deterministic decision replay, but it must not be described as a Strategy A profitability backtest.

## Next implementation layer

Once the source-confirmed execution semantics are frozen, an execution simulator can consume replay decisions and candles to produce fills and outcomes. The outcome ledger already exists and can then become the accounting layer for R-based statistics.
