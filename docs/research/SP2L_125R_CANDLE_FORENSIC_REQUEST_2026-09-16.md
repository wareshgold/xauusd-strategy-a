# SP2L 125R Candle Forensic Request — 2026-09-16

## Objective

Trace the persisted 1min observation at `2026-08-20 20:54:00` back to its exact candle sequence and intermediate Strategy A objects before making any geometry judgment.

## Persisted observation

- direction: SELL
- entry: `4521.5838`
- stopLoss: `4521.61331`
- TP1: `4517.8892399999995`
- risk distance: `0.02951`
- R: `125.19688241535353`

## Required reconstruction

1. Identify the spike candidate indices and OHLC values feeding the correction detector.
2. Identify `correctionStartIndex`, `correctionExtremeIndex`, `direction`, and `extremePrice`.
3. Identify the first trigger candle after the correction extreme and its OHLC/close.
4. Verify that the trigger close equals the persisted Entry.
5. Verify that the correction extreme equals the persisted Stop.
6. Reconstruct Leg-1 size and TP1 from the current experimental projection implementation.
7. Record every intermediate value without changing any rule.

## Decision rule

This document is forensic only. It must not promote an implementation rule to canonical geometry. If source evidence does not uniquely discriminate Entry/SL anchoring, the geometry remains `UNRESOLVED`.

## Constraint

Do not introduce a minimum stop distance, spread adjustment, buffer, wick/body preference, or other threshold solely to remove the extreme-R observation.
