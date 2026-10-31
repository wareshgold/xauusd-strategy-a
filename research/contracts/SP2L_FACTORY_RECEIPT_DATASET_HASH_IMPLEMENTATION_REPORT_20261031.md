# Receipt Dataset Hash Contract — Implementation Report — 2026-10-31

## Scope and baseline

- Branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Base branch: `research/factory-candidate-lab-20261010`
- Base commit: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Implementation status: focused implementation complete; awaiting PR review.
- This change is Factory provenance infrastructure only. It does not alter Strategy A geometry, canonical rules, candidate selection, optimization, or production decisions.

## Implemented contract

1. `ExecutionReceipt` preserves its original eight positional fields and appends:
   - `receipt_schema_version` (default 1)
   - `dataset_content_sha256` (default null)
2. Schema v1 serialization includes `receipt_schema_version: 1` and omits the digest key. A v1 receipt cannot carry a digest.
3. Schema v2 serialization always includes `dataset_content_sha256`; dataset-backed receipts require lowercase 64-character SHA-256, while trusted synthetic receipts use explicit JSON null.
4. Historical `input_fingerprint` semantics remain unchanged. It is not reinterpreted as a raw dataset digest.
5. Dataset-backed Discovery and Stability adapters attach the exact SHA-256 they compute from the dataset artifact bytes.
6. The built-in exact-type `SyntheticExecutionAdapter` emits schema v2 with explicit null. Subclasses and wrappers do not inherit the synthetic exception.
7. `ResearchJobRunner` rejects schema-v1 receipts for new dataset-verified evidence with `LEGACY_UNVERIFIED`; it compares schema-v2 dataset hashes to the runner-observed hash. Only the exact built-in synthetic adapter may use null.
8. New evidence stores `receipt_schema_version` and `dataset_content_sha256` in `EvidenceBundle.result`; its summary revision is `RECEIPT_METRICS_V2`.
9. The runner derives the new summary revision from the receipt schema. An explicit incompatible revision override fails closed. The Orchestrator no longer defaults to a hard-coded V1 summary revision.
10. Evidence acceptance and end-to-end research provenance compare the v2 receipt fields to the corresponding evidence fields. Historical `result_revision` values remain opaque for schema-v1 evidence; schema version and evidence result revision are not conflated.
11. The standalone synthetic E2E helper now uses the trusted built-in synthetic adapter rather than a custom adapter that mislabeled an externally computed dataset hash as its input fingerprint.
12. `ResearchRecord` remains unchanged: its evidence fingerprint transitively binds the updated evidence payload.

## Test changes

- Added schema-v1/v2 serialization checks.
- Added malformed digest rejection.
- Added synthetic explicit-null assertions.
- Added runner tests for legacy-v1 rejection and dataset-hash mismatch.
- Updated dataset-backed fake adapters in Discovery, Stability, Validation, and Holdout tests to provide the exact dataset hash.
- Added receipt-focused tests to `.github/workflows/factory-tests.yml`.

## CI evidence

At commit `80edbe4f4293a57bec048e92b3dfa095b3ed16b5`:
- Factory Research Tests: **PASS — 151 passed in 1.73s**
- Factory Journal Lock Cross-Platform Tests (Ubuntu + Windows): **PASS**
- SP2L forensic deterministic checks: **PASS**

The focused Factory suite and the listed cross-platform/deterministic workflows are green. The entire repository test suite was not run, so this is not a claim of full-repository validation.

## Compatibility and safety boundaries

- Existing eight-argument positional receipt construction remains source-compatible.
- Legacy schema-v1 receipts remain representable/readable as v1 but are never promoted by the new runner to dataset-verified evidence.
- Existing v1 evidence result revisions are not rewritten or inferred from receipt schema.
- A null digest is not inferred from a missing key.
- No dataset artifact, runtime journal, live runner, MT5 state, or research geometry was modified.
- No BUY/SELL or production decision capability was added.

## Remaining review items

- Review the exact-type synthetic trust boundary and the V1 rejection policy before merge.
- Run the complete repository test suite in the normal local development environment if required by the project’s release process.
- Do not merge this PR solely on the basis of the focused CI run.
