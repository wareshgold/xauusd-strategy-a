# SP2L G49 — Historical Coverage Contract

Date: 2026-09-09
Status: IMPLEMENTED — CI REQUIRED
Scope: strategy-neutral research infrastructure only

## Objective

Move from a single 5,000-row real-data sample to a reproducible historical dataset acquisition plan without introducing Strategy A geometry, BUY/SELL detection, optimization, or performance-based source selection.

## Contract

1. Historical requests are expressed as explicit timezone-aware UTC start/end boundaries.
2. For regular intervals, each acquisition chunk contains at most the provider point limit.
3. Chunks are deterministic and non-overlapping: the next chunk starts exactly one interval after the previous chunk end.
4. Chunk indices are contiguous and deterministic.
5. Naive datetime boundaries are rejected; timezone provenance must be explicit.
6. Overlapping, gapped, reversed, or otherwise non-contiguous chunk boundaries are rejected.
7. Provider response quality remains governed by the existing acquisition and quality-audit contracts.
8. Raw and normalized fingerprints remain the identity mechanisms for acquired artifacts; retrieval timestamp is provenance, not a substitute for content identity.
9. DEV/VAL/FRESH_HOLDOUT date boundaries must be explicitly chosen and recorded before canonical validation; this gate does not choose those dates by performance.
10. No Strategy A detector, candidate geometry, optimization, or profitability claim is introduced.

## Implementation

`research/engine/coverage.py` provides deterministic chunk planning and boundary validation. Tests cover determinism, maximum-point chunking, timezone requirements, and overlap/non-contiguity rejection.

## Gate decision

G49 infrastructure is ready for CI validation. Historical acquisition itself is a subsequent runtime operation and must preserve each raw response and manifest. A successful G49 CI run does not constitute Strategy A validation or Frozen Geometry resolution.
