# SP2L Factory Snapshot — Cross-Process Journal Write Lock — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-CROSS-PROCESS-JOURNAL-LOCK-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Parent research state: `SP2L_FACTORY_PREAPPEND_JOURNAL_INTEGRITY_GUARD_20261028`
- Scope: serialize cooperating persisted-journal writers across the integrity preflight, append, and rollback window.
- Status at snapshot creation: implementation and new tests committed; CI verification was in progress.

## Changes

1. `src/strategy_factory/job_events.py`
   - Added an OS-backed sidecar lock at `<journal-name>.lock`.
   - Windows uses `msvcrt.locking`; POSIX uses `fcntl.flock`.
   - Holds the lock across persisted snapshot validation, in-memory/persisted equality checking, append, flush/fsync, and rollback if writing fails.
   - The lock sidecar is intentionally persistent and is not deleted; deleting it could allow cooperating processes to lock different file identities.
   - Existing fail-closed behavior remains: stale, corrupt, missing unexpectedly, or divergent journal snapshots are not automatically repaired or overwritten.

2. `tests/test_forward_preparation.py`
   - Added a stale-ledger test: a second ledger instance cannot append after another instance has advanced the persisted journal; the journal bytes remain unchanged.
   - Added a spawned cross-process test proving the second cooperating process cannot enter the journal critical section until the first releases the lock.

## Commits

- Cross-platform cooperative lock: `e4555b1aaa960e62e2699535c8dce7ab84e1c848`
- Literal correction for lock sentinel and JSONL newline: `6f64620f0df0533a54fd2455314c91b02b8113df`
- Final lock-byte/newline correction: `dc54a9c2001d746a82a0ffa2aa406e61bd653d53`
- Stale-writer and process-serialization tests: `3e80f74c08a54c8e2f4343760a599877d4fa8b4f`

## Verification

- `Factory Research Tests`: run started for test commit; final result to be confirmed.
- `SP2L forensic deterministic checks`: run started for test commit; final result to be confirmed.
- No local test execution is claimed in this snapshot.

## Boundaries and remaining risk

- This lock coordinates only writers that use this helper and the same sidecar path. A process that edits or appends directly to the JSONL file without taking the sidecar lock can still race; this is not a filesystem-wide access-control boundary.
- Windows and POSIX code paths are implemented, but a CI result from one platform does not prove runtime behavior on every platform. Confirm both Windows and POSIX runners before calling cross-platform behavior fully validated.
- The lock file is a coordination artifact, not a strategy-evidence event. It remains on disk by design.
- The journal SHA-256 remains an integrity fingerprint, not a signed attestation.
- No automatic repair or historical journal rewrite was added. No MT5/forward-test process was touched. No Strategy A geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules changed. No PR was merged.
- These tests validate software coordination and evidence-preservation behavior only; they do not establish a statistical trading edge or live execution safety.
