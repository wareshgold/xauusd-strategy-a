# Receipt Schema Versioning and Persistence Boundary Decision — 2026-10-31

- Status: source-audited design decision proposal; not implementation and not canonical.
- Branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Audited baseline: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Scope: choose where receipt schema version and dataset content digest belong without breaking historical evidence identity.

## 1. Source findings

The current code has three distinct serialization boundaries:

1. **ExecutionReceipt** (`src/strategy_factory/execution.py`)
   - Immutable in-memory dataclass with eight fields.
   - Exposes `as_dict()`.
   - Has no `from_dict()`, schema version, or receipt persistence ledger.
   - Existing tests and callers construct it positionally with eight arguments.

2. **EvidenceBundle** (`src/strategy_factory/evidence.py`)
   - Stores a JSON-serializable `result` mapping and `result_revision`.
   - Its canonical `as_dict()` and fingerprint include the complete `result` mapping.
   - Has no `from_dict()` in the inspected module.
   - `ResearchJobRunner` currently persists a selected receipt summary in `EvidenceBundle.result`: execution ID, engine revision, input fingerprint, semantics and metrics. It does not store the full receipt.

3. **ResearchRecord** (`src/strategy_factory/research_record.py`)
   - Has explicit `record_revision`, `as_dict()` and `from_dict()`.
   - Binds `evidence_fingerprint`, `run_fingerprint`, dataset identity and audit/snapshot fingerprints.
   - Does not store the full receipt. Its fingerprint already transitively binds the EvidenceBundle fingerprint.

Other relevant findings:
- `ResearchJobRunResult` is an in-memory aggregate, not a receipt serializer.
- Runner's evidence result is the durable selected receipt summary boundary.
- ResearchRecord should not duplicate receipt fields: its evidence fingerprint already binds the complete evidence payload.
- Current eight-position receipt construction is widespread in tests, so any dataclass additions must be appended after existing fields with defaults.

## 2. Version placement decision

**Proposed version owner: ExecutionReceipt serialization.**

Add two appended dataclass fields, preserving all existing positional arguments:

- `receipt_schema_version: int = 1`
- `dataset_content_sha256: str | None = None`

Serialization rules:

| Schema | Serialized keys | Meaning |
|---|---|---|
| v1 | `receipt_schema_version=1`; no `dataset_content_sha256` key | Legacy receipt; dataset observation is unknown |
| v2 dataset-backed | `receipt_schema_version=2`; `dataset_content_sha256` is a lowercase 64-character SHA-256 string | Adapter claims it read and verified those exact artifact bytes |
| v2 synthetic | `receipt_schema_version=2`; `dataset_content_sha256=null` | Trusted built-in SyntheticExecutionAdapter did not observe dataset bytes |

Compatibility reader rule for a future deserializer: a historical serialized receipt with neither version nor dataset digest key is interpreted as v1 only. A v2 receipt missing the digest key is malformed. Explicit null is never inferred from absence.

The v1 serialization shape must omit the dataset digest key. Do not serialize a null digest on v1, because that would erase the distinction between legacy absence and explicit v2 non-observation.

No generic `execution_identity` field is introduced here. Dataset digest identifies bytes only; engine, fixture, parameters, strategy and semantics remain independently bound by their existing identities/fingerprints.

## 3. Evidence persistence rule

The runner's `EvidenceBundle.result` must mirror the receipt's schema and dataset observation as first-class fields:

- `receipt_schema_version`
- `dataset_content_sha256` (present for v2, including explicit null for synthetic)
- existing `execution_id`, `engine_revision`, `input_fingerprint`, `execution_semantics`, `metrics`

The evidence `result_revision` must identify the summary layout (proposed `RECEIPT_METRICS_V2` for new v2 evidence). Do not silently reinterpret existing `RECEIPT_METRICS_V1` records. The runner's default revision and explicit caller overrides must be audited before implementation; an override must not permit a v1 summary to omit a v2 receipt's digest.

ResearchRecord remains at its existing revision unless its own serialized fields change. Its `evidence_fingerprint` transitively binds the new summary; adding a duplicate dataset digest to ResearchRecord is unnecessary and risks two competing values.

## 4. Gate implications

- Dataset-backed v2 receipt: require valid lowercase SHA-256 and exact equality with the independently observed artifact digest and registered Dataset provenance.
- Trusted built-in synthetic v2 receipt: require explicit null, while preserving Runner's pre-adapter Dataset Registry check and job fingerprint binding.
- v1 legacy receipt: classify LEGACY_UNVERIFIED. It may be inspected and retained historically, but cannot be upgraded to VERIFIED by reading the current registry later.
- v2 missing key, malformed digest, or null from a dataset-backed adapter: reject as missing/invalid required evidence.
- No evidence bundle may be accepted as dataset-verified solely because its run-level dataset fingerprint passed. Receipt-level adapter observation is a separate claim.

The receipt gate, acceptance gate and end-to-end provenance result must agree on this classification. Do not let one gate report PASS while another considers the receipt legacy or unbound.

## 5. Compatibility and migration constraints

1. Keep the original eight dataclass fields in their current order.
2. Append the two new fields; never insert them between existing positional fields.
3. Preserve the exact historical meaning of `input_fingerprint`.
4. Keep v1 serialized payloads distinguishable from v2 explicit null.
5. Do not add a deserializer until its callers and persisted formats are inventoried; current `ExecutionReceipt` has none.
6. Do not change ResearchRecord revision or fingerprint payload unless its serialized structure changes.
7. Evidence fingerprints will change for new v2 summaries because the result mapping changes. Historical evidence fingerprints remain immutable.
8. Any export/dashboard/consumer that reads `EvidenceBundle.result` must tolerate both V1 and V2 layouts and must not infer a missing v1 digest as null.
9. `result_revision` is not a substitute for `receipt_schema_version`: the former versions the evidence summary, the latter versions the receipt contract.
10. No implementation should be applied to the base branch or PR #365 as part of this design-only change.

## 6. Implementation sequencing

1. Complete consumer inventory for `EvidenceBundle.result` and any external JSON readers before editing.
2. Add receipt fields and version-aware serialization while retaining positional compatibility.
3. Update adapter builders: dataset-reading adapters pass the digest they independently computed; the trusted built-in synthetic adapter passes explicit null under v2.
4. Add runner-side trusted adapter classification and compare adapter digest with runner/registry digest.
5. Add receipt classification to acceptance and end-to-end provenance gates.
6. Persist the schema/digest fields in the evidence summary and version its result layout.
7. Add V1/V2 consumer compatibility tests and the synthetic contract cases.
8. Run focused and full Factory tests; verify evidence/research-record determinism and legacy fixture behavior.
9. Record test commands and actual outputs before claiming any gate passes.

## 7. Remaining unresolved consumer audit

The source-level inventory above covers the core Python object graph. Before implementation, a repository-wide search in the actual checkout is still required for:
- direct `EvidenceBundle.result` field access outside the inspected runner/tests;
- serialized evidence JSON consumed by scripts/dashboard/export paths;
- any external caller depending on exact `ExecutionReceipt.as_dict()` key sets;
- persisted `result_revision` values and historical fixture files.

GitHub code search exposed no matches for the targeted identifiers in this repository during this audit, so absence of additional consumers is **not** established. This is an explicit pre-implementation check, not a claim that the consumer inventory is complete.

No source code, tests, data, live runner, or production behavior was changed. No tests were executed.
