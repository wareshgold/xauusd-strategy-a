# SP2L Factory Snapshot — Cross-Process Journal Write Lock — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-CROSS-PROCESS-JOURNAL-LOCK-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Parent research state: `SP2L_FACTORY_PREAPPEND_JOURNAL_INTEGRITY_GUARD_20261028`
- Scope: serialize cooperating persisted-journal writers across the integrity preflight, append, and rollback window.
- Status: implementation, tests, cross-platform CI, and snapshot committed; focused journal-lock tests passed on Ubuntu and Windows, and Factory Research Tests passed on the latest test commit.

## Changes

1. `src/strategy_factory/job_events.py`
   - Added an OS-backed sidecar lock at `<journal-name>.lock`.
   - Windows uses `msvcrt.locking`; POSIX uses `fcntl.flock`.
   - Holds the lock across persisted snapshot validation, in-memory/persisted equality checking, append, flush/fsync, and rollback if writing fails.
   - The lock sidecar is intentionally persistent and is not deleted; deleting it could allow cooperating processes to lock different file identities.
   - A follow-up source audit corrected and explicitly tests the single-byte Windows lock sentinel and actual JSONL newline terminator.
   - Existing fail-closed behavior remains: stale, corrupt, missing unexpectedly, or divergent journal snapshots are not automatically repaired or overwritten.

2. `tests/test_forward_preparation.py`
   - Added a stale-ledger test: a second ledger instance cannot append after another instance has advanced the persisted journal; the journal bytes remain unchanged.
   - Added a spawned cross-process test proving the second cooperating process cannot enter the journal critical section until the first releases the lock.
   - Added injected `fsync` failure tests: a failed append flush rolls bytes back to the prior boundary and does not commit in-memory state; if rollback `fsync` also fails, the code raises a manual-reconciliation error rather than claiming durable recovery.
   - Added a persisted-journal end-to-end test that follows a synthetic fresh holdout through Forward Gate preparation, bound-forward lifecycle, and reconciliation while checking the exact audited journal prefix hash remains bound and production authorization stays false.
   - The lock-sentinel assertion is platform-specific: Windows requires the one-byte sentinel; POSIX `flock` permits an empty sidecar.

3. `.github/workflows/factory-journal-lock.yml`
   - Added a focused matrix job on `ubuntu-latest` and `windows-latest`, running `tests/test_forward_preparation.py` on Python 3.12.
   - First matrix attempt exposed an overly Windows-specific test assertion on POSIX; the assertion was corrected without changing production lock behavior. The next matrix run passed on both OSes.

## Commits

- Cross-platform cooperative lock: `e4555b1aaa960e62e2699535c8dce7ab84e1c848`
- Literal correction for lock sentinel and JSONL newline: `6f64620f0df0533a54fd2455314c91b02b8113df`
- Final lock-byte/newline correction: `dc54a9c2001d746a82a0ffa2aa406e61bd653d53`
- Stale-writer and process-serialization tests: `3e80f74c08a54c8e2f4343760a599877d4fa8b4f`
- Literal correctness fix: `b3256a3fef70ce4e913fd07a94338502f5b00613`
- Explicit JSONL terminator/lock-sentinel test: `b63c5da350927d319e7ec0b764e20c991e12c23e`
- Cross-platform journal lock workflow: `9f9311ee90a7a43aedbcc930b75deb560e2150bc`
- Platform-specific sentinel expectation: `d38d4493392962b3f13ec0b925a450be3b5483e4`
- Corrected Windows sentinel literal: `0425204e8adebf1cb7edbe7a1f1d9e9211818552`
- Append/rollback `fsync` fault-injection tests: `70219df91a63def7085c048c47254d912d8f1e96`
- Persisted-journal Forward Gate to reconciliation E2E test: `88337ca01aded1b569012dcd7c0bc6e6ec7d47e6`
- E2E assertion correction using the public runtime result contract: `feb26e65704b3b3364b6da1d6cc4f1216e0f028e`

## Verification

- At test commit `3e80f74c08a54c8e2f4343760a599877d4fa8b4f`: Factory Research Tests PASS (run 1161); SP2L forensic deterministic checks PASS (run 671).
- At initial snapshot commit `8b894af07e3cdbf021a16be67e760ba1258302bf`: Factory Research Tests PASS (run 1163); SP2L forensic deterministic checks PASS (run 672).
- At final code/test commit `b63c5da350927d319e7ec0b764e20c991e12c23e`: Factory Research Tests PASS (run 1171); SP2L forensic deterministic checks PASS (run 676).
- Initial cross-platform matrix run `40663528066`: Windows PASS; Ubuntu failed because the test incorrectly expected a Windows-only sentinel byte on POSIX. This was a test expectation issue, not a lock failure.
- After correcting the assertion, matrix run `40663809519`: `journal-lock-tests (ubuntu-latest)` PASS and `journal-lock-tests (windows-latest)` PASS.
- At corrected test commit `0425204e8adebf1cb7edbe7a1f1d9e9211818552`: Factory Research Tests PASS (run `40663809638`).
- At fault-injection test commit `70219df91a63def7085c048c47254d912d8f1e96`: Factory Research Tests PASS (run `40665077614`); journal-lock/preparation matrix PASS on Ubuntu and Windows (run `40665077637`).
- The first persisted-journal E2E attempt exposed a test-only assumption that the runtime result exposed its session object. The assertion was corrected to check the prepared session, which is the public contract.
- At corrected E2E test commit `feb26e65704b3b3364b6da1d6cc4f1216e0f028e`: Factory Research Tests PASS (run `40665486537`); journal-lock/preparation matrix PASS on Ubuntu and Windows (run `40665486446`).
- Verification is CI-based; no local test execution is claimed.

## Boundaries and remaining risk

- This lock coordinates only writers that use this helper and the same sidecar path. A process that edits or appends directly to the JSONL file without taking the sidecar lock can still race; this is not a filesystem-wide access-control boundary.
- The focused locking/preparation suite now passes on both Ubuntu and Windows hosted runners. This validates the tested code paths on those runner images, not every filesystem, network share, or process that bypasses the helper.
- The lock file is a coordination artifact, not a strategy-evidence event. It remains on disk by design.
- The journal SHA-256 remains an integrity fingerprint, not a signed attestation.
- No automatic repair or historical journal rewrite was added. No MT5/forward-test process was touched. No Strategy A geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules changed. No PR was merged.
- These tests validate software coordination and evidence-preservation behavior only; they do not establish a statistical trading edge or live execution safety.
