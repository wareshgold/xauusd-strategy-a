# SP2L MT5 Historical Acquisition Runbook — 2026-09-17

## Purpose

Define the reproducible procedure for acquiring older XAUUSD M1 history from the same MT5 research source used by the existing non-overlap stability snapshots.

This is a data-acquisition and provenance document only. It does not define Strategy A geometry or execution semantics.

## Target source condition

The existing stability study used:

- provider: MetaTrader5 terminal API
- terminal/server: Otet Group MT5 Terminal / OtetGroup-MT5
- symbol: XAUUSD.ecn
- timeframe: M1
- requested bars per snapshot: 10,000
- P-Gap price: 1.0
- spike multiplier: 1.5
- max SL price: 10.0
- TP: 1R
- requested snapshot-end spacing: 12 days

The acquisition process must not alter the downstream strategy configuration.

## Acquisition procedure

1. Use the same MT5 terminal/server and exact symbol identity where available.
2. Request raw M1 bars covering the target historical period.
3. Record the request start/end or snapshot-end rule before retrieval.
4. Preserve provider timestamps and normalize them to UTC without changing the represented instant.
5. Record actual first/last bar timestamps and actual bar count.
6. Audit chronological ordering and M1 continuity.
7. Count and report missing/discontinuous bars; never fabricate missing candles.
8. Materialize the exact raw dataset used for research.
9. Compute SHA-256 over the materialized artifact.
10. Record the acquisition code revision and downstream runner/configuration identifier.
11. Only after the artifact passes the provenance/data-quality gate may it enter non-overlap stability analysis.

## Required manifest

Each acquired artifact must have a sidecar manifest containing:

- dataset_id;
- source/provider;
- terminal/server;
- account-independent symbol identity;
- timeframe;
- requested interval;
- actual first/last UTC timestamps;
- requested bar count;
- actual bar count;
- gap count and gap ranges;
- retrieval timestamp UTC;
- artifact path/name;
- artifact SHA-256;
- acquisition code revision;
- downstream runner revision;
- frozen configuration identifier;
- audit status.

## Audit status values

- `ACQUIRED_UNAUDITED`
- `AUDITED_PASS`
- `AUDITED_FAIL`
- `REJECTED_UNVERIFIABLE`

Only `AUDITED_PASS` artifacts may be used for published stability results.

## Reproducibility rule

If the exact MT5 bars cannot be recovered or independently verified from the recorded artifact and hash, the corresponding result must remain explicitly unverifiable.

A different provider, symbol, timeframe, or undocumented terminal history must not silently replace the target dataset.

## Historical expansion target

The next intended coverage extension is older non-overlapping windows preceding the existing July–September study, subject to actual MT5 availability. April/May/June must not be claimed as covered until an audited artifact proves their availability.

## Promotion boundary

Successful data acquisition does not validate Strategy A. It only makes additional historical observations eligible for the same frozen research configuration. Geometry, fill semantics, and production authorization remain independently gated.
