# Dataset Contract and Fingerprint — 2026-09-14

## Purpose

This layer makes replay inputs auditable and reproducible. It does not define or validate Strategy A rules.

## Contract

Each research dataset is identified by:

- dataset ID and version;
- source/provider identity;
- schema version;
- symbol and timeframe;
- timezone and timestamp convention;
- row count;
- first and last timestamp;
- SHA-256 content fingerprint.

The fingerprint is calculated from a deterministic canonical serialization of timestamp, open, high, low, and close for every row in order.

## Boundary

A fingerprint proves content identity, not data quality, market completeness, broker/feed equivalence, or source authority. Different XAUUSD providers must therefore retain distinct source identities and be compared explicitly rather than silently treated as interchangeable.

No production dataset fingerprint is asserted by this change. The tests use synthetic rows only.

## Replay integration

`ReplayRunManifest` now records `datasetFingerprint` alongside dataset ID/version. A replay result can therefore identify exactly which dataset content produced the run.

## Strategy-A status

This is infrastructure only. It does not promote P-Gap geometry, A/B/C/D anchors, pending-limit fill semantics, structural stop boundaries, target mapping, or any other unresolved Strategy A interpretation into canonical rules.
