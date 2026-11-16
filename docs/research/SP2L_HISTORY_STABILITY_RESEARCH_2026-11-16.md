# SP2L Repeated History Observation Stability — Research Model (2026-11-16)

**Status:** offline research implementation; synthetic validation pending  
**Canonical status:** non-canonical; no production caller  
**Runtime boundary:** no MT5 import, terminal access, broker calls, filesystem I/O, or Runner integration

## Purpose

Compare two independently captured history-evidence observations for the same account/session/server and exact query interval. The question is whether the supplied order/deal counts and externally computed payload fingerprints remained identical across distinct observations.

## Fingerprint boundary

This model deliberately does **not** define how raw MT5 rows are serialized or hashed. The fingerprint producer must supply:
- a stable algorithm identifier;
- an order payload SHA-256;
- a deal payload SHA-256;
- a unique observation identifier.

The fingerprint algorithm and raw-payload canonicalization remain unresolved. This avoids inventing row ordering, serialization, field selection, or fill/reconciliation semantics. A digest is accepted as an external claim; this model does not recompute or verify it.

## Comparison rules

Both observations must independently classify as `OBSERVED_CONSISTENT_FOR_SCOPE` under the completeness evidence classifier. Their account/session/server, interval, time basis/source, package version, and terminal build must match. Observation IDs and observed-at values must differ. Per-observation manifest hashes and timestamps may differ.

Outcomes:
- `INVALID_OBSERVATION`
- `INSUFFICIENT_DISTINCT_OBSERVATIONS`
- `SCOPE_MISMATCH`
- `FINGERPRINT_METHOD_MISMATCH`
- `CHANGED_BETWEEN_OBSERVATIONS`
- `STABLE_ACROSS_OBSERVATIONS`

## Interpretation

`STABLE_ACROSS_OBSERVATIONS` means only that the two supplied snapshots have matching counts and matching externally supplied payload fingerprints under the same declared fingerprint method and scope. It does not prove that either snapshot is complete, that API calls were atomic, or that the broker archive contains no additional records.

The helper `stability_proves_history_completeness` deliberately always returns false. No output from this model may set `history_completeness_verified=True`.

## Validation

Synthetic tests cover stable and changed payloads/counts, account/scope mismatches, method mismatches, duplicate observation identity/time, invalid hashes, and invalid underlying evidence. Local test execution is pending.
