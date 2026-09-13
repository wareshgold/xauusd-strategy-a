# G388 — Deterministic Dataset Runner

Date: 2026-09-13

## Status

**INFRASTRUCTURE PASS CANDIDATE; CANONICAL STRATEGY DEV REMAINS BLOCKED.**

G388 consumes an abstract candle stream and deterministically reports temporal split counts, ordering, duplicate timestamps, leakage status, and canonical trade count.

## Guarantees

- chronological ordering is explicitly checked;
- duplicate timestamps are explicitly detected;
- DEV/VAL/HOLDOUT assignment is deterministic;
- identical inputs produce identical results;
- no Strategy A geometry is inferred;
- canonical trade generation is hard-coded to zero in this infrastructure layer.

## Research boundary

This runner is intentionally strategy-agnostic. It does not detect spikes, P-Gaps, corrections, A/B/C/D points, entries, stops, targets, or fills.

Therefore it cannot establish profitability and must not be interpreted as a backtest.

## Next gate

After CI verification, the next useful step is to connect the audited snapshot through a read-only dataset adapter and emit a reproducibility report. Canonical DEV remains unavailable until Frozen Geometry is resolved.
