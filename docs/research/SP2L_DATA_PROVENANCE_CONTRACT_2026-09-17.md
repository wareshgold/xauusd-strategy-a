# SP2L Research Data Provenance Contract — 2026-09-17

## Purpose

Define the minimum provenance record required for any future historical dataset used in SP2L stability, untouched validation, robustness, or holdout research.

This is a data-audit contract. It does not define or modify Strategy A geometry.

## Required dataset identity

Every research dataset or snapshot must record:

- provider/data source;
- terminal or server identity when applicable;
- symbol identity;
- timeframe;
- requested start/end or snapshot-end definition;
- retrieval timestamp in UTC;
- requested bar count;
- actual first and last bar timestamps in UTC;
- actual bar count;
- timezone normalization rule;
- missing/discontinuous-bar findings;
- file/content SHA-256 when a materialized file is used;
- code/runner revision used to acquire or transform the data;
- configuration identifier for the downstream research run.

## Acquisition rule

Historical coverage expansion must use the same research configuration already frozen for the relevant comparison. Dataset expansion must not be used as an opportunity to optimize Strategy A parameters.

## Integrity rule

A dataset used for a published research result must be reproducible from its provenance record or accompanied by the materialized artifact and its cryptographic hash.

If the exact underlying bars cannot be verified, the result must be treated as unverifiable for that dataset rather than silently substituted with another source.

## Gap rule

Missing or discontinuous bars must be measured and reported. No synthetic candle may be inserted into the research dataset unless a separate fixture explicitly tests a transformation that is itself source-authorized and documented.

## Snapshot rule

For rolling/non-overlap stability research, each snapshot must preserve:

1. the exact snapshot-end rule;
2. the exact requested bar count/window rule;
3. the exact source and symbol;
4. the exact strategy configuration;
5. the exact code revision.

Changing any of these creates a different research condition and must not be silently mixed with prior results.

## Promotion boundary

Provenance completeness does not establish strategy validity. It only establishes traceability of the data used for a research result.

Source-resolution, Frozen Geometry, untouched validation, robustness/stability, and fresh-holdout gates remain independent.
