# SP2L Factory Snapshot — Byte-Level Forward Event Journal Binding — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-FORWARD-GATE-BYTE-LEVEL-JOURNAL-BINDING-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Parent: `SP2L_FACTORY_FORWARD_GATE_EVENT_LEDGER_SNAPSHOT_20261028`
- Scope: bind Forward readiness to byte-level evidence for the event-ledger snapshot, without journal repair or rewrite.
- Status: implemented; both repository CI workflows passed; not merged.

## Changes

1. `src/strategy_factory/forward_gate_factory.py`
   - Gate context now requires a valid lowercase SHA-256, non-negative byte size, and an explicit snapshot source (`persisted_jsonl` or `in_memory`).
   - A persisted source must include its path; an in-memory source must not claim a persisted path.
   - The Gate result records the journal SHA-256, byte size, event count, source, and optional path as audit metadata.

2. `src/strategy_factory/forward_preparation.py`
   - For persisted ledgers, calls `inspect_job_journal_snapshot`, which reads one byte snapshot, hashes those exact bytes, validates/parses the journal, and returns events parsed from that same snapshot.
   - Fails closed if the journal is missing, unreadable, invalid, or differs from the in-memory event tuple. It performs no repair, normalization, or write.
   - For explicit in-memory ledgers, calculates a deterministic JSONL byte representation and its SHA-256; labels the source as `in_memory` so it cannot be confused with a persisted file digest.

3. Tests
   - Added coverage that the persisted journal digest equals the exact byte prefix audited by the Gate (the later Forward handoff event is appended after the gate).
   - Added a corruption fixture that proves the preparation fails closed and leaves the corrupted journal bytes unchanged.
   - Added a negative test for malformed byte-level snapshot metadata.
   - Existing duplicate-completion, invalid sequence, identity, and no-production-decision tests remain in place.

## Implementation commits

- Gate metadata: `9bda178229c907c720c0a3fb1cf7c16f317e3d55`
- Persisted/in-memory snapshot capture: `a52c6cca0617b327edb871f87b2d77ad71a4a7e7`
- Test metadata and serialization fixtures: `c03c897c7dc4df9a3de37141ce290c68e5a84b63`, `b71ea2b6231d6f5e7a843dab0524c802367bbb5a`, `22c9a31157f6672b9b4c9c3a7a2828d7ae556b5d`
- Persisted snapshot tests: `c7f2b95bf2d0b28b7f7c227b8b548cab446f990e`, `ef23a619992a03cb4330c29afb6fd7dfaca5f21c`
- Corruption/no-repair test: `2524a7571595fae249ba8d46df095c050a0b69c4`, `61ccab1086f688e7bb328995bc2bd3ce0edd0223`

## Verification

At `61ccab1086f688e7bb328995bc2bd3ce0edd0223`:
- Factory Research Tests: PASS
- SP2L forensic deterministic checks: PASS

These are deterministic software-contract checks, not proof of a statistical trading edge or live execution safety.

## Boundaries

- A raw SHA-256 is integrity evidence for the bytes read at that moment, not a signed external attestation or proof that no external process changes the file afterward.
- The Gate is fail-closed when the persisted bytes do not parse or do not match the in-memory event tuple. It does not attempt recovery or repair.
- In-memory test/research ledgers are explicitly labeled and hashed from their deterministic JSONL serialization; this is not represented as a persisted-file digest.
- No historical journal was rewritten by the implementation. No MT5/forward-test process was touched. No Strategy A geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules were changed. No PR was merged.
