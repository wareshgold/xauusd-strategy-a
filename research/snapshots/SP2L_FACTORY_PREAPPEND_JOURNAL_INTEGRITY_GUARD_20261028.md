# SP2L Factory Snapshot — Pre-Append Journal Integrity Guard — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-PREAPPEND-JOURNAL-INTEGRITY-GUARD-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Parent: `SP2L_FACTORY_FORWARD_GATE_BYTE_LEVEL_JOURNAL_BINDING_20261028`
- Scope: fail closed before appending to a persisted Factory event journal that is corrupt, missing unexpectedly, or divergent from the in-memory ledger.
- Status: implementation and deterministic CI passed; not merged.

## Changes

1. `src/strategy_factory/job_events.py`
   - Before appending, re-reads and validates the persisted JSONL snapshot.
   - Requires the persisted events to equal the ledger's current in-memory event tuple.
   - Rejects corrupt, truncated, missing-with-nonempty-memory, or structurally valid but divergent journals before writing.
   - Does not repair or overwrite the source file.

2. `src/strategy_factory/forward_preparation.py`
   - Converts append integrity failures into a fail-closed `ForwardPreparationError`, explicitly requiring manual reconciliation.

3. `tests/test_forward_preparation.py`
   - Added a test where the file is corrupted externally after the ledger is loaded; verifies preparation fails before appending and the bytes and in-memory entries remain unchanged.
   - Added a test where the file is replaced by a different but structurally valid journal; verifies the same fail-closed/no-write behavior.
   - Retained prior tests for persisted byte-prefix hash binding and invalid-journal preservation.

## Commits

- Append preflight guard: `d2dc004f32e41861326f2c7fa9949ffccb75e393`
- Preparation error boundary: `300c9f9b55cf6f4338827087163badea9086f14d`
- External corruption test: `16c7134915256988cdfef2c206e8dd6f6a50cf46`
- Structurally valid divergence test: `fbdf9f8c2649ce6b5695e33d878f8972f078a00a`

## Verification

At `fbdf9f8c2649ce6b5695e33d878f8972f078a00a`:
- Factory Research Tests: PASS
- SP2L forensic deterministic checks: PASS

## Boundaries

- The pre-append check catches drift that exists when the check runs. It is not an inter-process lock; a separate writer could still race between the preflight read and append. A future change should define a supported cross-platform locking/coordination contract before claiming race-free multi-process safety.
- The SHA-256 describes the exact byte snapshot read at audit time and is not a signed attestation.
- No automatic repair or historical journal rewrite was added. No MT5/forward-test process was touched. No Strategy A geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules changed. No PR was merged.
- Passing CI establishes deterministic software-contract checks only, not a statistical trading edge or live execution safety.
