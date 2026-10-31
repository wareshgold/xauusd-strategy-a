# PR #375 Independent Self-Review Findings — 2026-10-31

- Reviewed PR head: `d2b6c15597e0b1ad720f1e8afbc80ada67724c0f`
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/375
- Review scope: receipt serialization, dataset-backed adapters, synthetic adapter boundary, Runner, Acceptance, research provenance, and related tests.
- Review outcome: **CHANGES REQUIRED — NOT APPROVED**
- No merge performed.

## Blocking finding: Acceptance/provenance do not independently verify dataset content identity

### Evidence in source

1. `src/strategy_factory/runner.py` lines 165–168 compares a non-synthetic receipt's `dataset_content_sha256` with the runner's `observed_content_sha256`. This protects the normal Runner path.
2. `src/strategy_factory/acceptance.py` lines 32–40 checks that schema-v2 evidence has the expected summary revision/schema and that its `dataset_content_sha256` equals the receipt's value. It does not compare that value with an independently observed or registered dataset content SHA, and it does not receive synthetic adapter classification/purpose/role.
3. `src/strategy_factory/research_provenance.py` line 106 repeats the receipt/evidence equality check but does not independently verify the digest against dataset content identity or enforce the synthetic-only exception.
4. `ExecutionReceipt.validate()` intentionally allows schema-v2 explicit null at the model layer; the trusted synthetic exception is enforced in Runner, not in the standalone gates.

### Failure mode

A schema-v2 dataset-backed receipt with `dataset_content_sha256 = null` can pass the digest-related checks in standalone Acceptance and Provenance if the Evidence result mirrors that null. Equality of two copies does not establish that the adapter observed the registered dataset bytes.

This means a caller invoking these gates outside the normal Runner path can receive PASS for a receipt that is not independently dataset-verified. It also falls short of the approved architecture requiring Runner and Acceptance Gate to compare independent dataset identities.

### Required correction

- Pass an independently derived dataset-content verification result / expected content SHA into the Acceptance and Provenance boundaries, or introduce an equivalent typed contract.
- For dataset-backed schema-v2 receipts, require a valid digest equal to the independently observed and registered artifact content SHA.
- Permit explicit null only for the exact built-in `SyntheticExecutionAdapter`, with purpose `SYNTHETIC_INFRASTRUCTURE_TEST` and DEVELOPMENT dataset role.
- Add direct Acceptance and Provenance negative tests for null and mismatching digests. Mirroring a bad receipt value into Evidence must not make the gate pass.
- Preserve legacy v1 readability without promoting it to dataset-verified status.
- Keep all current Runner checks fail-closed.

## Other reviewed areas

- Receipt schema v1/v2 serialization and original eight positional dataclass fields: no additional blocking issue found in inspected code.
- Discovery and Stability adapters preserve the composite `input_fingerprint` and populate a separate dataset digest.
- Exact-type synthetic adapter restriction and pre-run guard are present in Runner.
- Evidence V2 summary revision is bound to receipt schema in Runner and Acceptance.
- No Strategy A geometry, canonical SP2L rules, or production decision capability was changed.

## Review limitations

- This was a source-level review of the changed implementation and targeted tests; the full repository test suite was not run by this review.
- Focused CI at the reviewed head had passed previously (153 Factory Research tests, cross-platform Journal Lock, forensic deterministic checks). Those results do not cover the newly identified standalone-gate failure mode.
- GitHub rejected submitting a formal REQUEST_CHANGES review because the connected repository identity is the PR author ("Review Can not request changes on your own pull request"). The finding is recorded here; no approval or merge was attempted.

## Decision

PR #375 must remain unmerged until the Acceptance/Provenance independent-verification gap is corrected and the targeted tests/CI pass at the new head.


## Follow-up verification — 2026-10-31

The blocking finding above was corrected on PR #375. The original finding remains preserved as the reason for the follow-up.

- Corrected PR head: `e1fe34078b87b8e6d2a41eb38dfa8910c5206808`
- `DatasetProvenanceResult` now carries `registered_content_sha256` and `observed_content_sha256` independently of the composite fingerprint.
- Acceptance and Research Provenance both call the same strict receipt/dataset identity policy:
  - Dataset-backed V2: receipt digest must be non-null and equal both raw registered and observed SHA-256 values.
  - Synthetic null: exact built-in adapter type, exact `SYNTHETIC_INFRASTRUCTURE_TEST` purpose, DEVELOPMENT role, and explicit null receipt digest.
  - Subclasses/wrappers do not inherit the null exception.
  - V1 remains readable but acceptance reports `dataset_verified=false`; the new Runner path rejects V1.
- Direct negative tests cover mirrored null and mirrored mismatching digest at both standalone gates; Acceptance tests also cover exact synthetic allowance and subclass rejection.
- Validation Factory fixtures now pass the required adapter/purpose context.

### CI at corrected head

| Workflow | Run ID | Result |
|---|---:|---|
| Factory Research Tests | 41195484996 | success — 159 passed in 1.93s |
| SP2L forensic deterministic checks | 41195484997 | success |
| Factory Journal Lock Cross-Platform Tests | 41195485002 | success — Ubuntu and Windows |

An earlier run at an intermediate head exposed two Validation Factory fixture failures because the standalone Provenance gate now requires explicit adapter/purpose context. The fixtures were corrected, and all three workflows passed at the corrected head.

### Current decision

- The specific standalone-gate gap is **corrected in code and covered by focused tests/CI**.
- The full repository test suite remains unrun.
- PR #375 remains OPEN, Ready for review, mergeable, and **not merged**.
- No independent human approval has been recorded. The connected GitHub identity is the PR author, so a formal self-authored REQUEST_CHANGES review is unavailable.
- Human review and explicit user authorization are still required before merge.

This follow-up does not establish statistical edge, canonical SP2L geometry, untouched validation, Fresh Holdout completion, or production readiness.
