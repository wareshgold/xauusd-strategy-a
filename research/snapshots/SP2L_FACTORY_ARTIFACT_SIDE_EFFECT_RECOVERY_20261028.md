# SP2L Factory Snapshot — Artifact Side-Effect Interruption Recovery — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-ARTIFACT-SIDE-EFFECT-RECOVERY-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Test commit: `b2ed1cc2427a1aaa30cb45e4e7a85c800ebdacdc`
- Scope: synthetic process interruption after a side-effect artifact is persisted but before the executor returns a completion receipt.
- Status: Factory Research Tests PASS; SP2L forensic deterministic checks PASS; journal-lock cross-platform run PASS on Ubuntu and Windows. This is evidence-integrity validation only.

## Added test

File: `tests/test_factory_artifact_side_effect_interruption.py`

`test_existing_artifact_with_dispatched_only_journal_is_never_requeued`:
1. Submit a synthetic job; journal durably records `QUEUED` then `DISPATCHED`.
2. The injected executor writes a synthetic artifact file and raises `SystemExit` before returning a completion receipt.
3. Re-load the journal as a new process would.
4. Recovery reports `INTERRUPTED_REVIEW_REQUIRED`.
5. Queue reconstruction planning rejects the interrupted job with `not safe for queue reconstruction`.
6. Artifact bytes and journal lifecycle remain unchanged; executor call count remains one.

This demonstrates that artifact existence alone is not accepted as proof of a valid terminal completion, and the current recovery planner does not silently replay the interrupted job.

## CI on test commit

- Factory Research Tests: PASS — run `40669165680`
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40669165680
- SP2L forensic deterministic checks: PASS — run `40669172749`
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40669172749
- Factory Journal Lock Cross-Platform Tests: PASS — run `40669165720`
  - Ubuntu: PASS
  - Windows: PASS
  https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40669165720

Verification is CI-based; no local test execution is claimed.

## Limits and non-goals

- This test uses a synthetic local artifact and does not define a production artifact receipt format or an external artifact-discovery protocol.
- It does not prove exactly-once execution of arbitrary external side effects. The ambiguous DISPATCHED-only boundary remains manual-reconciliation-only.
- No automatic replay, queue reconstruction, journal repair, or artifact deletion was added.
- No MT5, Strategy A entry logic, unresolved SP2L geometry, production decision path, or live forward-test process was touched.
- No PR was merged.
- No statistical trading edge or production readiness is inferred.
