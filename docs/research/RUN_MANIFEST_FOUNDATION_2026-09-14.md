# Replay Run Manifest Foundation — 2026-09-14

## Purpose

Make every replay/backtest execution auditable and reproducible without encoding any unresolved Strategy A geometry.

## Required identity

A manifest records:

- run identifier;
- dataset identifier and dataset version;
- strategy identifier and strategy version;
- execution policy identifier;
- symbol and timeframe;
- start/completion timestamps;
- candle, signal, blocked and no-signal counts;
- execution-event count;
- ambiguous execution-event count.

## Determinism

The manifest serializer uses stable object-property order from the typed manifest and JSON indentation. It performs no metric calculation and no parameter selection.

## Source boundary

`executionPolicy` is an explicit run-level identifier. It does not imply that the policy is canonical Strategy A. Until source-confirmed fill, intrabar, stop and target semantics are frozen, research runs must label the execution policy as experimental/test infrastructure.

## Gate impact

This advances reproducibility infrastructure only. It does not promote any unresolved geometry to canonical status and does not constitute DEV, VAL, robustness, fresh-holdout, or production validation.
