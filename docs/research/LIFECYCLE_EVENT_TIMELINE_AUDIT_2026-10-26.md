# Lifecycle Event Timeline Audit Fixtures — 2026-10-26

## Purpose

This research-only fixture audits timestamp and identity anomalies in a supplied event sequence. It preserves the input sequence and does not establish a broker-canonical causal ordering.

## Findings

- Missing event timestamps remain explicitly missing.
- A timestamp regression in the supplied order is flagged without sorting the records.
- Different events sharing a millisecond are marked ambiguous; source row order is preserved but not treated as proof of event causality.
- Duplicate or empty event identifiers are reported and not deduplicated.
- A clean monotonic sequence is only a diagnostic result, not proof that causal order or broker history completeness is established.

## Test scope

Synthetic cases cover monotonic timestamps, same-millisecond ambiguity, timestamp regression, missing timestamps, duplicate IDs, empty IDs, and empty input. These tests do not read real broker history or change a live runner.

## Replay gate

No historical replay was run. Broker event timestamps may have different granularity and ordering guarantees; the fixture does not infer fills, combine partial deals, resolve late-arriving history, or define ordering when timestamps collide. Those semantics require source and broker evidence.
