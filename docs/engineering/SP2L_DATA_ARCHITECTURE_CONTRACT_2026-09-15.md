# SP2L Data Architecture Contract — 2026-09-15

## Status

`ARCHITECTURE_CONTRACT_ONLY`

This document defines the separation between research-market data and the eventual MetaTrader 5 (MT5) runtime. It does **not** define Strategy A geometry, execution semantics, or production BUY/SELL behavior.

## Source-aligned repository context

The repository README currently identifies **Twelve Data XAU/USD** as the initial research data candidate. It states that **M1 is intended to be the raw source of truth** and that **M5 should be derived locally from M1** so candle boundaries remain deterministic. The README also states that API credentials must never be committed.

This existing repository direction is retained, but this contract explicitly separates research data from the eventual MT5 production data path.

## Architectural principle

Twelve Data and MT5 are data/runtime environments, not authorities for Strategy A meaning.

Canonical Strategy A semantics must continue to follow:

`SOURCE → HUMAN ADJUDICATION → FROZEN GEOMETRY`

Neither historical-data optimization nor broker/terminal behavior may be used to resolve an unresolved source-geometry dimension.

## Two data planes

### 1. Research data plane

Purpose: reproducible research, deterministic replay, statistical validation, robustness/stability analysis, untouched validation, and fresh holdout.

Conceptual flow:

```text
Research Provider (initial candidate: Twelve Data XAU/USD)
        ↓
Raw Immutable M1 Dataset
        ↓
Deterministic Local Candle Derivation
        ↓
Research Replay / Backtest Engine
        ↓
Statistical Validation
```

Research data requirements:

- preserve provider provenance;
- preserve raw timestamps and OHLC values;
- preserve symbol/timeframe metadata;
- make M5 derivation deterministic from M1 where M5 is required;
- record missing/duplicate/invalid observations rather than silently repairing them;
- make dataset identity reproducible with version/hash metadata;
- keep API credentials outside the repository;
- never alter Strategy A geometry to fit the research dataset.

### 2. MT5 runtime/validation plane

Purpose: verify the frozen Strategy A implementation against the market data and execution environment supplied by MT5/broker infrastructure.

Conceptual flow:

```text
Broker / MT5 Historical Data
        ↓
MT5 Strategy Tester
        ↓
Strategy A EA
        ↓
Validation / Implementation Comparison
```

For live operation:

```text
Broker Market Feed
        ↓
MT5 Terminal
        ↓
Strategy A EA
        ↓
Broker Execution
```

The production EA should not require Twelve Data to supply ordinary market candles unless a future, separately approved architecture explicitly chooses an external data dependency.

## No Twelve Data → MT5 forwarding requirement

The default architecture does **not** require:

```text
Twelve Data → MT5 → Strategy A
```

Twelve Data is a research-data candidate. MT5 is the eventual execution/runtime environment. They are separate adapters around the same frozen Strategy A specification.

## Canonical engine boundary

The Strategy A rule implementation must be independent of the research provider and MT5 transport layer.

Conceptually:

```text
                    FROZEN STRATEGY A
                           │
                ┌──────────┴──────────┐
                │                     │
        Research Data Adapter    MT5 Data/Runtime Adapter
                │                     │
          Twelve Data*             MT5/Broker
                │                     │
        Research Replay          MT5 Tester / Live EA

* initial research candidate, not a permanent provider commitment
```

The adapters may normalize data into a common internal candle/event representation, but they must not introduce undocumented Strategy A rules.

## Validation responsibilities

### Research validation

Research validation answers questions such as:

- Is the frozen rule set reproducible?
- Does it show a statistical edge?
- Is the edge stable across time/regimes?
- Does it survive untouched validation?
- Does it survive a fresh holdout?

### MT5 validation

MT5 validation answers questions such as:

- Does the EA implement the frozen specification correctly?
- Does MT5 candle/tick behavior expose implementation differences?
- Are broker-specific symbol, spread, and execution characteristics represented?
- Does the MT5 Strategy Tester reproduce the intended event ordering without lookahead?

A successful research backtest is **not** by itself proof that a live MT5 deployment is equivalent. Conversely, MT5 tester performance must not be used to invent or resolve source geometry.

## Data equivalence boundary

Before comparing research results with MT5 results, the project must explicitly document any differences in:

- symbol identity and contract specification;
- timestamp/timezone/session semantics;
- OHLC construction;
- M1/M5 aggregation;
- missing or duplicate candles;
- bid/ask availability;
- spread;
- tick history and tick reconstruction;
- slippage/fill behavior;
- market-session boundaries.

No undocumented reconciliation rule may be silently introduced.

## Freeze dependency

This contract does not authorize deterministic Strategy A execution.

The intended ordering remains:

```text
SOURCE RESOLUTION
    ↓
EVIDENCE CANDIDATE INTAKE
    ↓
HUMAN MANUAL ADJUDICATION
    ↓
FROZEN GEOMETRY READINESS
    ↓
SEPARATE CANONICAL FREEZE DECISION
    ↓
DETERMINISTIC RESEARCH ENGINE
    ↓
UNTOUCHED VALIDATION
    ↓
ROBUSTNESS / STABILITY
    ↓
FRESH HOLDOUT
    ↓
MT5 IMPLEMENTATION / TESTER VALIDATION
    ↓
PRODUCTION AUTHORIZATION
```

The current repository is still before canonical geometry freeze. Therefore this document is an architecture boundary only.

## Explicit prohibitions

This contract does not authorize:

- a P-Gap formula;
- entry/fill semantics;
- Leg-2 anchor selection;
- structural invalidation boundary;
- pending-order refresh thresholds;
- AB=CD anchors or tolerance;
- target/2X formulas;
- bearish symmetry by inference;
- broker-specific buffers as Strategy A rules;
- production BUY/SELL decisions;
- using Twelve Data or MT5 backtest performance to resolve source ambiguity.

## Decision

**Adopt the two-plane architecture:** Twelve Data (initially) for controlled research data and MT5/broker data for eventual terminal validation/live runtime, with a provider-independent frozen Strategy A specification between them.

No permanent dependency on Twelve Data is authorized by this document.
