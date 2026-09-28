# SP2L FX Symbol Selection Research — 2026-09-28

## Purpose

Research diagnostic to compare FX candidates after MT5 FX Discovery Matrix execution.

This document does not promote any symbol or configuration to canonical Strategy A. It is a stability and selection aid only.

## Input

- `artifacts/backtest-mt5-fx-discovery/SP2L_MT5_FX_DISCOVERY_MATRIX_20260928T051034Z.csv`

## Evaluation dimensions

For each symbol/configuration:

- trade count
- win rate
- net R
- profit factor
- drawdown
- estimated USD P/L at 0.01 lot
- concentration sensitivity
- leave-one-symbol-out robustness

## Current observations

The discovery matrix indicates that:

- P-Gap 1.0 produced the largest aggregate FX discovery surface in the tested matrix.
- USDJPY produced the largest contribution in the current matrix and requires concentration review.
- Very high win-rate rows with low trade counts must not be treated as reliable candidates.

## Promotion rule

No FX symbol becomes part of Strategy A until:

1. geometry remains source-aligned,
2. validation is completed on untouched data,
3. stability and concentration checks pass.

## Next implementation step

Add a deterministic analyzer that converts matrix R results into 0.01 lot USD estimates using MT5 symbol specifications (tick value, tick size, contract data) rather than fixed assumptions.
