# SP2L Provider-Neutral Engine Boundary — 2026-09-15

## Status

`NON-CANONICAL ENGINEERING DESIGN`

This document defines a future implementation boundary only. It does not define Strategy A geometry.

## Boundary

```text
Provider-specific data
        ↓
Data Adapter / Normalizer
        ↓
Normalized Candle Contract
        ↓
Strategy A deterministic engine
        ↓
Observation / validation result
        ↓
Runtime-specific adapter (if applicable)
```

The strategy engine must not know whether a candle originated from Twelve Data, MT5, or another explicitly approved source.

## Adapter responsibilities

An adapter may:

- acquire source data;
- map source symbols to the normalized identity;
- normalize timestamps;
- normalize numeric representation without changing price meaning;
- construct deterministic derived timeframes from an explicitly approved base series;
- preserve provenance;
- report missing/duplicate/out-of-order input.

An adapter must not:

- detect P-Gap using provider-specific assumptions;
- choose entry anchors;
- alter candles to improve signals;
- add strategy thresholds or buffers;
- infer execution/fill behavior;
- convert an unresolved source dimension into a provider-specific rule.

## Engine responsibilities

After canonical geometry is frozen, the deterministic engine may evaluate only the frozen specification against normalized candles.

The engine must not branch on provider identity to change Strategy A meaning.

## MT5 implementation

The MT5 EA is an implementation/runtime adapter around the same frozen Strategy A specification. MT5-specific market data and execution concerns remain outside canonical strategy meaning.

The MT5 Strategy Tester is a validation environment; it is not a source-of-truth mechanism for resolving ambiguous source geometry.

## Research implementation

The research replay engine is a validation environment using reproducible research data. Twelve Data is the current repository-documented research candidate, not a production-provider commitment.

## Required future conformance test

Once geometry is frozen, create provider-neutral fixtures where the same normalized candle sequence is supplied through both research and MT5-facing adapters. The strategy observation must match exactly for identical normalized input.

Any mismatch must be localized to:

1. acquisition;
2. normalization;
3. runtime/execution;
4. or a documented implementation defect.

It must not be resolved by silently changing Strategy A geometry.
