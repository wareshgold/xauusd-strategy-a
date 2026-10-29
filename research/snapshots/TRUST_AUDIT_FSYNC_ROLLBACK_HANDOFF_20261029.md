# Trust Audit Append Rollback — Official Handoff Snapshot

**Snapshot date:** 2026-10-29  
**Repository:** `wareshgold/xauusd-strategy-a`  
**PR:** [#368 — require source-ready frozen geometry before Fresh Holdout](https://github.com/wareshgold/xauusd-strategy-a/pull/368)  
**PR state at snapshot:** Open, Draft, not merged  
**Working branch:** `fix/fresh-holdout-readiness-gate-20261029`

## Exact checkpoint

- **PR head commit:** `63a0cee3d0c41d79f551f4931ea71b0e84acb564`
- **Source update commit:** `02e6f5b8cf1aba36d2831b461bf6b73c61110f68`
- **Test update commit:** `63a0cee3d0c41d79f551f4931ea71b0e84acb564`
- **PR base branch:** `research/factory-candidate-lab-20261010`
- **Base SHA observed:** `a39877d4f3c04e71890792995ac82ef1b76e4823`

## Change recorded

File: `src/strategy_factory/trust_audit.py`

The append path now captures the file's byte size before writing. If append write/flush/fsync raises `OSError`, it truncates back to the captured size, flushes, and fsyncs the rollback. It reports a rollback-confirmed error only if that rollback fsync succeeds. If rollback or rollback fsync raises `OSError`, it raises `TrustAuditError` with **manual reconciliation required** and includes both errors.

Tests added in `tests/test_trust_audit.py`:

1. Inject append-fsync failure, allow rollback fsync, assert the visible file bytes equal the original bytes and the error reports rollback.
2. Inject failure for both append fsync and rollback fsync, assert manual reconciliation is required and the visible bytes are restored in this test environment; durability remains unconfirmed.

## CI observed for PR head `63a0cee3d0c41d79f551f4931ea71b0e84acb564`

Checked on 2026-10-29:

- **Factory Research Tests:** completed, conclusion `success` (run 40873033639, run #1449).
- **SP2L forensic deterministic checks:** completed, conclusion `success` (run 40873033601, run #884).
- **Factory Journal Lock Cross-Platform Tests:** completed, conclusion `success` (run 40873033614, run #276); Linux and Windows jobs both succeeded.

These are workflow-level results. The new tests are included in the Factory Research Tests run, but no separate per-test report was retrieved in this checkpoint. Do not overstate this as independently inspected test-case output.

## Safety and unresolved limitations

- This is an audit-file failure-handling change only; it does not define SP2L geometry or production trade rules.
- Successful `fsync` is not an absolute hardware/filesystem durability guarantee.
- Rollback does not provide an atomic transaction across Trust Audit and the separate journal.
- If rollback cannot be confirmed, stop and manually reconcile the audit file and related journal before retrying any transition.
- PR #368 remains Draft and unmerged. No production eligibility or live execution authorization is implied.

## Next actions

1. Verify this snapshot commit and confirm PR head after the snapshot commit lands.
2. Retrieve the Factory Research Tests job/step output or run the focused Trust Audit tests in a controlled checkout to explicitly confirm both new tests.
3. Recheck CI at the latest PR head, including any reruns triggered by the snapshot commit.
4. Keep the PR Draft until the focused evidence and review are complete; do not merge automatically.

## Resume prompt

Continue from this snapshot. First verify the live GitHub state for PR #368 and this snapshot file. Do not assume the recorded SHA is still the current head after this snapshot is committed. Then obtain explicit evidence for the two new Trust Audit rollback tests, check current CI, and update this handoff without changing canonical SP2L rules or enabling production.


---

## Follow-up checkpoint — 2026-10-29

This addendum supersedes the earlier "Next actions" section where it conflicts with the status below.

### Current code and test commits

- **Current PR head before this snapshot update:** `5f2cad558144593c7544f01d352dce22a6ec9788`
- **Rollback implementation commit:** `02e6f5b8cf1aba36d2831b461bf6b73c61110f68`
- **Rollback tests commit:** `63a0cee3d0c41d79f551f4931ea71b0e84acb564`
- **Factory CI inclusion commit:** `27918c2325c872d57ea2a55946b868c5ffd424bc`
- **Trust Audit test-fixture correction commits:** `62d9624dc85fabe50c7d3e2a7912940d39f1d323`, then `5f2cad558144593c7544f01d352dce22a6ec9788`.

### Why CI was changed

The original Factory focused pytest command did **not** include `tests/test_trust_audit.py`; the prior green run therefore did not prove the new rollback tests had executed. The workflow `.github/workflows/factory-tests.yml` was updated to include that test module.

The first run with the module included exposed three existing test-fixture/assertion mismatches, not failures in the two new rollback tests:
- recovery negative cases were attempted after a successful recovery had already been recorded, so the implementation correctly raised the already-recovered error first;
- the tamper fixture rewrote JSON with noncanonical spacing, so canonical-record validation failed before hash-chain validation;
- the multiline JSON fixture was invalid for JSONL and failed parsing before canonical-encoding validation.

The test fixtures were corrected to test each intended condition in the correct order and encoding. This was a test-quality correction; no production Trust Audit behavior was changed in those follow-up commits.

### Explicit CI evidence

For commit `5f2cad558144593c7544f01d352dce22a6ec9788`:

- **Factory Research Tests:** run #1453, run ID `40873702867`, completed `success`; job log reports **107 passed in 1.42s**. The executed command includes `tests/test_trust_audit.py`, so both rollback test cases were part of the successful suite.
- **SP2L forensic deterministic checks:** run #886, run ID `40873702840`, completed `success`.
- **Factory Journal Lock Cross-Platform Tests:** run ID `40873702893`, completed `success`; both Ubuntu and Windows jobs succeeded.
- The Factory run #1451 at commit `27918c2325c872d57ea2a55946b868c5ffd424bc` failed with **104 passed, 3 failed**. Run #1452 at commit `62d9624dc85fabe50c7d3e2a7912940d39f1d323` also failed on the same three test-fixture/assertion mismatches. Both failures are superseded by successful run #1453, but remain part of the audit trail.

### Current disposition

- PR #368 is still **open, Draft, and unmerged**.
- Keep it Draft pending review; do not merge automatically.
- The rollback behavior is covered by the successful Factory focused suite, but successful `fsync` remains no absolute hardware/filesystem durability guarantee.
- No cross-file atomic transaction between Trust Audit and the separate journal is provided.
- No canonical SP2L geometry, production eligibility, or live trading authorization is changed.

### Resume from here

1. Verify live PR head and rerun status after this snapshot update creates a new commit.
2. Review the diff for the Trust Audit implementation, the corrected fixtures, and CI inclusion.
3. Keep the PR Draft until review is complete. Do not merge or enable production on the basis of CI alone.


---

## Final follow-up — latest PR-head verification (2026-10-29)

### Verified current head and CI

The PR head at the start of this check was `1ba4565952a667d62ffddc04cf7432a7318ba97a`. PR #368 remains **open, Draft, and unmerged**, based on `research/factory-candidate-lab-20261010`.

All three GitHub Actions workflows completed successfully for that exact head:

- **Factory Research Tests** — run #1455, ID `40873925932`, success. Job log: **107 passed in 1.59s**.
- **SP2L forensic deterministic checks** — run #890, ID `40873925915`, success.
- **Factory Journal Lock Cross-Platform Tests** — run #282, ID `40873925896`, success; both Ubuntu and Windows jobs succeeded.

The Factory workflow command explicitly includes `tests/test_trust_audit.py`; the two rollback tests are part of the successful 107-test suite. The log's compact summary does not print individual test names, so the evidence is suite-level inclusion plus successful suite result, not a separate per-test line report.

### Review checkpoint

Reviewed the current Trust Audit append/rollback implementation, the test module, the Factory workflow inclusion, and the PR changed-file list. The code path catches write/flush/fsync `OSError`, attempts truncation to the pre-append byte size, flushes and fsyncs the rollback, and requires manual reconciliation if rollback cannot be confirmed. Tests assert both the successful rollback path and the uncertain rollback path.

No production-readiness claim follows from this review. Outstanding release gates documented above remain material: independent system trust-root/keyring provisioning and control, independent journal-source control, complete provenance binding, operational key lifecycle, and the lack of a cross-file atomic transaction between the audit ledger and event journal. Successful `fsync` is not an absolute hardware/filesystem durability guarantee.

### Disposition / next step

- No merge or PR state change performed.
- Keep PR #368 Draft while a maintainer reviews the full diff and the outstanding release gates.
- Before any later snapshot update or code edit, re-read the live PR head and CI; any new commit requires its own CI verification.
