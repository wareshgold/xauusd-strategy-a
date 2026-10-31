# Factory Forward Gate Event Ledger Snapshot — 2026-10-28

- Branch: `research/factory-candidate-lab-20261010`
- Scope: require a complete immutable tuple snapshot of lifecycle events at the Forward Gate.
- Status: implementation complete; deterministic CI passed; not merged.

## Implementation

- `forward_gate_factory.py`: added `source_event_ledger_snapshot`; missing snapshots fail closed; every event is validated and sequence continuity is required; the matching Holdout job/station must have exactly one `COMPLETED` event equal to the supplied source event; conflicting `FAILED` events are rejected.
- `forward_preparation.py`: passes `events.entries()` into the gate after recording the Holdout completion.
- `test_forward_gate_factory.py`: added negative tests for missing snapshots, duplicate Holdout completion, and invalid snapshot sequence/fingerprint. Rejection tests preserve the input tuple.

## Commits

- Gate validation: `7786f0fd974d4ecfd7c49886c1a9b23b7df38c52`
- Preparation wiring: `5fd092c2d8c4e6369fb9f8f0c094d06a9334a3d5`
- Tests: `e57a91d5787a234d829a1030c94fc20608bba3b1`
- Fixture correction: `3ed88a1b0509373e5139d8cb9a1c46732a7b4649`

## Verification

At `3ed88a1b0509373e5139d8cb9a1c46732a7b4649`:
- Factory Research Tests: PASS
- SP2L forensic deterministic checks: PASS

## Limitations

The tuple is validated using event fingerprints and sequence continuity; it is not a signed attestation of the complete persisted JSONL bytes. A later hardening step may bind persisted-journal snapshots to their byte-level SHA-256. The work did not change Strategy A geometry, rewrite historical journals, touch MT5/forward-test processes, or merge a PR. CI success is not evidence of a statistical trading edge.
