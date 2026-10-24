# SP2L Research / MT5 Data Adapter Contract — 2026-09-15

## Status

`NON-CANONICAL ENGINEERING CONTRACT`

This document defines the boundary between market-data providers and the SP2L Strategy A engine. It does not define Strategy A geometry, execution semantics, or production signals.

## 1. Architectural rule

The Strategy A specification must be provider-neutral after canonical geometry is frozen.

Research and MT5 are separate data/runtime planes:

```text
Research plane
Twelve Data (initial research candidate)
        ↓
raw M1 dataset
        ↓
deterministic M5 derivation where required
        ↓
research replay / statistical validation

                    FROZEN STRATEGY A
                           │
              provider/runtime-neutral core
                           │
        ┌──────────────────┴──────────────────┐
        ↓                                     ↓
Research adapter                       MT5 adapter
        ↓                                     ↓
research data                           MT5/broker data
        ↓                                     ↓
research validation                    MT5 Strategy Tester / runtime
```

There is no mandatory Twelve Data → MT5 forwarding path.

## 2. Research data plane

The repository README identifies Twelve Data XAU/USD as the initial research-data candidate and M1 as the intended raw source of truth. M5 is intended to be derived locally from M1 so candle boundaries remain deterministic.

Research data must retain provenance sufficient to reproduce:

- provider and symbol;
- timeframe and source granularity;
- timestamp convention and timezone;
- OHLC fields and any provider-specific fields used;
- retrieval window;
- retrieval timestamp;
- raw artifact identity/hash where available;
- transformation from M1 to derived M5;
- missing/duplicate/out-of-order handling.

Research data is not permitted to redefine Strategy A geometry.

## 3. MT5 data plane

The eventual MT5 implementation should consume the MT5 terminal/broker market data available to the EA and MT5 Strategy Tester.

The production architecture does not require Twelve Data to feed MT5.

MT5-specific behavior must be treated as an adapter/runtime concern, including broker symbol specifications, available history, spread, tick generation, and execution/fill behavior.

## 4. Shared canonical engine boundary

The Strategy A engine may consume only an explicit normalized market-data contract. Provider adapters may normalize data into that contract but must not add strategy-specific interpretation.

The normalized contract should preserve at minimum:

- timestamp;
- timeframe;
- open;
- high;
- low;
- close;
- source/provider identity;
- source symbol identity;
- deterministic candle sequence/index.

Any additional field must have an explicit provenance and purpose.

## 5. Cross-plane reconciliation

Research results and MT5 results are not assumed identical.

Before treating them as comparable, record differences in:

- symbol specification;
- price precision;
- timestamp/timezone/session boundaries;
- candle construction;
- historical coverage;
- missing/duplicate bars;
- spread and bid/ask availability;
- tick versus OHLC modeling;
- execution/fill assumptions.

A reconciliation report must distinguish data differences from strategy-implementation differences.

## 6. Validation sequence

This contract does not authorize implementation of Strategy A geometry. The required sequence remains:

`SOURCE RESOLUTION → HUMAN ADJUDICATION → FROZEN GEOMETRY → ENGINE IMPLEMENTATION → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Research-provider data may support research validation only after the relevant geometry is frozen.

MT5 Strategy Tester validation is a separate implementation/runtime validation layer and does not resolve source ambiguity.

## 7. Explicit prohibitions

This contract must not be used to:

- invent P-Gap formulas;
- choose entry/fill semantics;
- define AB=CD anchors or tolerances;
- define target/2X formulas;
- infer bearish symmetry;
- select buffers or thresholds from data;
- use backtest performance to adjudicate source meaning;
- authorize BUY/SELL production decisions.

## 8. Future acceptance criteria

The adapter boundary is acceptable only when:

1. identical canonical inputs produce identical Strategy A engine observations;
2. provider-specific normalization is isolated outside strategy logic;
3. raw research provenance is reproducible;
4. MT5-specific runtime behavior is isolated and documented;
5. cross-plane differences can be audited without changing canonical geometry;
6. no unresolved source geometry is hidden inside an adapter.

Until those conditions are met, the architecture remains engineering preparation only.
