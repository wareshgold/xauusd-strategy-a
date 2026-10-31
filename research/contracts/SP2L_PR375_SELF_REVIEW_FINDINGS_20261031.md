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
