# SP2L Live Integration Boundary — 2026-09-17

## Status

Research / engineering boundary only.

This document does **not** promote Strategy A to canonical status, does not freeze unresolved geometry, and does not authorize live BUY/SELL generation or order execution.

## Repository audit

Current research branch:

`research/sp2l-nonoverlap-stability-2026-09-17`

The repository already contains:

- a market-data client for Twelve Data under `src/infrastructure/market-data/`;
- application-level market-data aggregation;
- MT5-related execution-domain components under `src/execution/mt5/` for broker constraints and position-modification logic;
- execution state-machine tests.

The repository does **not** currently contain a verified MT5 terminal data adapter or a Telegram notification adapter. The presence of `src/execution/mt5/` must not be interpreted as a live MetaTrader connection.

The branch's environment example currently contains a Twelve Data API key and runtime setting only; no MT5 terminal connection settings or Telegram settings are defined.

## Required architecture boundary

The intended future production path is:

`MT5 terminal/feed -> normalized market data -> frozen SP2L engine -> signal validation/lifecycle -> notification adapter -> Telegram`

If order execution is ever authorized separately, it must be behind an additional broker-execution boundary and must not be implied by Telegram notification.

## Research-only mode

Before canonical geometry is frozen, any live-data integration may only support observation/research functions such as:

- ingesting and timestamp-normalizing bars;
- recording raw/normalized market observations;
- running non-canonical diagnostics;
- emitting `RESEARCH_EVENT` / `OBSERVATION` records;
- comparing live observations with frozen synthetic fixtures.

It must not emit canonical `BUY` or `SELL` decisions.

## Promotion gates

The following remain prerequisites for any production signal path:

1. source resolution for unresolved geometry, including F14 / AB=CD;
2. explicit resolution of execution/fill semantics;
3. frozen executable geometry;
4. deterministic synthetic fixture coverage;
5. untouched validation;
6. robustness/stability validation under a pre-registered protocol;
7. fresh holdout validation;
8. explicit production authorization.

No backtest result, including the current six-window descriptive stability result, may itself promote a rule to canonical status.

## Current finding

The correct next engineering step is to define adapters and interfaces without implementing production signal semantics. The correct next research step is to expand temporal stability coverage while preserving the existing implementation/configuration.

## Explicit non-goals

This boundary does not define:

- P-Gap formula;
- AB=CD anchors or tolerance;
- entry/fill semantics;
- replacement semantics;
- SL/invalidation geometry;
- TP2 geometry;
- Round Level geometry;
- production BUY/SELL criteria.

Those remain source-resolution items and must not be inferred from implementation convenience or backtest performance.
