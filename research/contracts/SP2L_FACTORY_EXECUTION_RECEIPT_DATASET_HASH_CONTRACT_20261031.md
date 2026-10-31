# Factory Execution Receipt Dataset Hash Contract — Design Draft

- Date: 2026-10-31
- Base branch: `research/factory-candidate-lab-20261010`
- Base commit: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Working branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Status: research design draft; not canonical, not implemented, not validated by tests.
- Scope: separate adapter input identity from exact dataset content identity without changing Strategy A/SP2L meaning.

## 1. Source facts established at the base commit

1. `ExecutionReceipt` currently contains `input_fingerprint`, but no independent `dataset_content_sha256`.
2. `build_execution_receipt` constructs that receipt and currently accepts the adapter's `input_fingerprint` only.
3. `DiscoveryMatrixAdapter` hashes the configured M1 artifact bytes, then checks that the Discovery output's `dataset_provenance.content_sha256` equals that hash. Its `input_fingerprint` is a hash of a larger canonical payload containing spec, script/configuration identifiers, output identity and dataset SHA.
4. `StabilityMatrixAdapter` hashes the configured M1 artifact bytes, checks the handoff-bound SHA and artifact ID, and includes dataset SHA plus Discovery/Stability output hashes in its composite `input_fingerprint`.
5. `ResearchJobRunner.run` receives `observed_content_sha256`, validates it against the Dataset Registry before calling the adapter, and later validates the adapter receipt. It does not currently compare a receipt dataset SHA to the runner-observed SHA.
6. `SyntheticExecutionAdapter` derives its `input_fingerprint` from a synthetic fixture and the test spec; it does not read dataset artifact bytes. It does include dataset metadata from the spec in its composite identity.
7. `DatasetArtifact.content_sha256` is the registered artifact byte digest. `DatasetIdentity.fingerprint` is a different digest over dataset metadata plus content fingerprint. These values must not be conflated.

These are source observations at the stated base commit, not claims about later commits or runtime behavior.

## 2. Contract decision proposed

Keep `input_fingerprint` unchanged in meaning.

Add an independent `dataset_content_sha256` to the versioned Execution Receipt contract:

- For a dataset-backed adapter, it is the lowercase SHA-256 of the exact artifact bytes the adapter verified as the dataset input to its execution.
- For an explicitly synthetic infrastructure adapter that did not read a real dataset artifact, it is explicitly null in the new receipt schema.
- Absence of the field in a legacy receipt is not equivalent to explicit null in a new receipt.
- A 64-character hexadecimal string is syntactically valid; it is not, by itself, proof that the adapter actually consumed those bytes.

### Schema compatibility

Recommended serialization rule:

- Receipt schema v1: legacy shape; `dataset_content_sha256` key absent.
- Receipt schema v2: `dataset_content_sha256` key required; value is either a valid SHA-256 string or explicit null under the synthetic-only policy.
- A missing field in v2 is malformed and must not be normalized to null.
- A v1 receipt remains readable for historical inspection. Do not rewrite it, infer its dataset SHA from `input_fingerprint`, or promote it to dataset-verified status.
- Do not retroactively change historical acceptance decisions. New gates may report a separate evidence/provenance status for legacy receipts.

The exact serialization envelope and version field placement must be confirmed against all persisted receipt consumers before implementation.

## 3. Adapter observation policy

The adapter contract must state whether the adapter is expected to observe a real dataset artifact. This policy must be explicit and machine-checkable, not inferred from whether the receipt field happens to be null.

### Dataset-backed execution

- Adapter reads or independently verifies the exact immutable artifact bytes.
- Adapter emits `dataset_content_sha256`.
- Runner independently compares the receipt value with its own `observed_content_sha256` and the registered artifact identity.
- Acceptance fails on missing, malformed, or mismatching dataset hash for a dataset-backed adapter.
- Discovery/Stability must preserve their existing composite `input_fingerprint`; they must not replace it with the raw dataset hash.

### Synthetic infrastructure execution

- Synthetic fixture identity remains distinct from real dataset identity.
- The synthetic adapter emits explicit null for `dataset_content_sha256` in schema v2 because it does not read dataset bytes.
- The fixture itself must have a deterministic fixture identity/content digest in the synthetic test evidence.
- Synthetic mode is allowed only in explicitly designated infrastructure/contract tests. It must not be a bypass for dataset-backed research, holdout, or production-oriented acceptance.
- The current runner still performs its independent Dataset Registry/provenance checks before invoking the synthetic adapter. This proposal does not remove or weaken those checks.

The mechanism for declaring/enforcing adapter observation policy (for example a typed capability or a trusted adapter classification) is an implementation decision to resolve before code changes. An arbitrary adapter must not be able to self-label as synthetic to evade dataset binding.

## 4. Gate outcome semantics

Dataset-content verification must be reported independently from execution-identity validation.

Recommended provenance outcomes:

- `VERIFIED`: dataset-backed v2 receipt digest equals the runner-observed digest and registered artifact identity.
- `MISMATCH`: receipt, runner-observed digest, or registered artifact digest disagree.
- `MISSING_REQUIRED_EVIDENCE`: dataset-backed v2 receipt lacks the required digest or has malformed data.
- `LEGACY_UNVERIFIED`: v1 receipt is readable, but has no independent adapter-observed dataset digest.
- `NOT_APPLICABLE`: explicit synthetic v2 receipt under the approved synthetic-only policy; this is not a dataset verification PASS.

Do not collapse `LEGACY_UNVERIFIED` or `NOT_APPLICABLE` into `VERIFIED`. Whether a particular workflow may proceed with those statuses is a separate policy decision; fresh holdout and dataset-backed evidence must not be granted verified status without the required evidence.

## 5. Execution identity boundary

Do not add a standalone `execution_identity` field in this change.

The current receipt already records execution ID, test ID, strategy revision, execution semantics, engine revision and input fingerprint. The test spec/run carry additional declared parameters and dataset metadata. Before claiming full reproducibility, audit whether the persisted evidence bundle retains every required component and stable adapter identity.

If a later change proposes a canonical execution identity digest, it must first define:
- canonical serialized fields and normalization;
- adapter identity/version and engine revision semantics;
- parameter and fixture inclusion;
- dataset identity versus dataset content digest;
- schema-version behavior;
- deterministic serialization and independent recomputation.

No digest formula is defined in this draft.

## 6. Synthetic fixture matrix

All cases below are infrastructure tests with controlled bytes and deterministic fixture inputs. They do not model SP2L geometry or trading outcomes.

| ID | Adapter mode | Receipt field | Expected result |
|---|---|---|---|
| F01 | Dataset-backed, matching bytes | Correct SHA-256 | VERIFIED |
| F02 | Dataset-backed, changed artifact bytes | Different SHA-256 | MISMATCH |
| F03 | Dataset-backed, receipt digest differs from runner observation | Valid but different SHA | MISMATCH |
| F04 | Dataset-backed v2, digest missing | Key absent | MISSING_REQUIRED_EVIDENCE / malformed v2 |
| F05 | Dataset-backed v2, malformed digest | Wrong length or non-hex | MISSING_REQUIRED_EVIDENCE |
| F06 | Dataset-backed v2, explicit null | null | MISSING_REQUIRED_EVIDENCE |
| F07 | Legacy v1 receipt | Dataset digest key absent | LEGACY_UNVERIFIED; readable, not upgraded |
| F08 | Synthetic v2 fixture | Explicit null + fixture identity | NOT_APPLICABLE; synthetic-only |
| F09 | Synthetic mode claims real dataset digest without reading it | SHA supplied without observation | Reject policy violation |
| F10 | Synthetic adapter used in dataset-backed holdout workflow | Explicit synthetic classification | Reject/blocked by workflow policy |
| F11 | Matching dataset SHA but changed engine/parameters | Same dataset digest, changed execution inputs | Dataset VERIFIED; execution identity comparison independently detects difference |
| F12 | Dataset registry/artifact mismatch despite matching adapter/runner SHA | Registered artifact differs | MISMATCH |

### Cross-cutting assertions

- Existing `input_fingerprint` values remain byte-for-byte/semantically unchanged.
- Discovery and Stability composite fingerprints remain composite.
- New schema v2 requires explicit presence of the dataset field.
- v1 deserialization and historical evidence inspection remain possible.
- No legacy fingerprint is reinterpreted as a dataset SHA.
- Dataset hash equality does not imply engine/configuration equality.
- Fixture hash is never substituted for a real dataset hash.
- Rejected cases do not mutate registries, receipts, journals, or source artifacts.
- All test artifacts are synthetic and isolated from development/validation/holdout datasets.

## 7. Implementation sequence after design review

1. Inventory every receipt serializer, deserializer, persisted consumer, and historical fixture.
2. Freeze the v2 serialization/versioning rule and trusted adapter observation-policy mechanism.
3. Add synthetic contract tests first, including legacy v1 behavior.
4. Add the optional receipt field and adapter population without changing `input_fingerprint`.
5. Add runner-side receipt-vs-observed-vs-registered digest comparison.
6. Add independent acceptance/provenance reporting for VERIFIED, MISMATCH, MISSING_REQUIRED_EVIDENCE, LEGACY_UNVERIFIED and NOT_APPLICABLE.
7. Run focused tests, full Factory Research Tests, forensic deterministic checks and relevant CI.
8. Capture a new immutable snapshot with exact commit SHA, test evidence and limitations.

## 8. Explicit non-goals

- No Strategy A geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics or execution rules.
- No dataset rewrite, historical receipt rewrite, registry migration or journal repair.
- No change to MT5/forward runners.
- No production BUY/SELL decisions or production authorization.
- No claim of statistical edge, validation success, or canonical SP2L rules.

This document is a proposed design contract only. It is not canonical until source-consumer inventory, synthetic fixtures, implementation and untouched validation are complete.
