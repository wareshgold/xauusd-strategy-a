# Synthetic Receipt Contract Test Specification — 2026-10-31

- Status: test-first specification; not executable tests and not an implementation.
- Design branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Audited source baseline: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Scope: prove the receipt's dataset-observation claim independently of its composite adapter input fingerprint.
- Non-goal: no Strategy A geometry, trading logic, or production decision behavior.

## 1. Source-grounded constraints

The current `SyntheticExecutionAdapter` hashes a canonical payload containing fixture, engine, test/spec, dataset metadata and parameters. It does not read dataset artifact bytes. The current `ResearchJobRunner` separately validates the supplied observed dataset SHA against the job fingerprint and Dataset Registry before invoking any adapter. Both facts must remain independently testable.

The current `ExecutionReceipt` has eight positional fields and an `as_dict()` method, but no receipt deserializer or schema-version field. The current `EvidenceBundle.result` stores a selected receipt summary rather than the complete receipt. Therefore these tests must not assume a universal persisted-receipt deserializer or invent a version-envelope location.

## 2. Trust boundary decision for synthetic mode

**Implemented boundary:** synthetic non-observation is granted by the Factory orchestration boundary only to the exact built-in `SyntheticExecutionAdapter` type, and only when the caller explicitly marks `purpose="SYNTHETIC_INFRASTRUCTURE_TEST"` on a `DEVELOPMENT` dataset. It is not granted by a receipt field, adapter-provided string, or freely overridable capability flag.

- Exact built-in adapter type + exact infrastructure purpose + `DEVELOPMENT` dataset role: synthetic infrastructure mode; its v2 receipt must carry explicit `dataset_content_sha256: null`.
- The runner rejects the built-in synthetic adapter before creating a research run or usage-ledger entry if the purpose is not exactly `SYNTHETIC_INFRASTRUCTURE_TEST` or the dataset role is not `DEVELOPMENT`.
- `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT` are therefore ineligible for synthetic non-observation, even if a caller supplies the infrastructure purpose.
- Every other adapter type, including subclasses/wrappers of the synthetic adapter: dataset-backed mode by default; its v2 receipt must carry a valid digest matching runner observation and registry evidence.
- A future need for another synthetic adapter requires an explicit trusted registration mechanism in a separate reviewed change. No self-declaration or caller-controlled boolean may silently bypass dataset binding.
- The runner's pre-execution Dataset Registry/provenance validation remains mandatory in both modes. Synthetic mode means only “adapter did not observe dataset bytes”; it does not waive runner validation or authorize research/holdout acceptance as dataset-verified.

This exact-type rule is deliberately conservative. It may constrain wrappers, but avoids treating an untrusted adapter assertion as proof of non-observation.

## 3. Test harness requirements

Use only temporary in-memory registries, deterministic fixtures and temporary byte artifacts. Do not use DEVELOPMENT, VALIDATION, FRESH HOLDOUT, production or user MT5 data. Tests must not mutate shared registries, journals, receipts or files.

Test helper requirements:
- Dataset byte fixture A and byte fixture B with distinct independently computed SHA-256 values.
- Registry registered to fixture A.
- Runner observed hash independently supplied as fixture A's digest.
- Adapter receipt construction must preserve the existing composite `input_fingerprint`; do not set it equal to dataset SHA as a shortcut.
- Synthetic fixture identity/content fingerprint must remain distinct from both dataset SHA and `input_fingerprint`.
- Keep positional construction compatibility for the existing eight-field `ExecutionReceipt` call sites.

## 4. Required contract tests

| ID | Test | Setup / assertion | Expected |
|---|---|---|---|
| S01 | Built-in synthetic receipt is explicit non-observation | Exact built-in synthetic adapter executes; serialized v2 receipt contains the dataset key with JSON null | PASS; status NOT_APPLICABLE |
| S02 | Synthetic input fingerprint remains composite | Change fixture ID or spec parameter; receipt `input_fingerprint` changes and is not treated as raw dataset SHA | PASS |
| S03 | Synthetic fixture identity is retained | Evidence retains deterministic fixture identity/digest independently of dataset SHA | PASS |
| S04 | Runner registry gate still runs for synthetic | Supply wrong runner-observed digest or wrong job dataset fingerprint | Runner rejects before adapter execution |
| S05 | Synthetic does not bypass registry mismatch | Registry points to A; runner observes B | Runner rejects; adapter call count remains zero |
| S06 | Exact built-in synthetic type is the only non-observation exception | A subclass/wrapper returns explicit null | Rejected as missing dataset digest for dataset-backed mode |
| S07 | Arbitrary adapter cannot self-label synthetic | Adapter adds a synthetic-looking attribute/receipt marker but is not the exact trusted type | Marker ignored; missing digest rejected |
| S08 | Dataset-backed matching receipt | Adapter reads fixture A and returns SHA(A); runner and registry also bind A | VERIFIED |
| S09 | Adapter/runner mismatch | Adapter returns SHA(B), runner/registry bind A | MISMATCH; no accepted evidence |
| S10 | Missing digest in v2 | Dataset-backed adapter returns a v2 receipt without the required key | Malformed/missing-required evidence; reject |
| S11 | Explicit null in dataset-backed v2 | Dataset-backed adapter returns null | MISSING_REQUIRED_EVIDENCE; reject |
| S12 | Malformed digest | Wrong length, non-hex, uppercase if lowercase is the specified canonical form, or non-string | MISSING_REQUIRED_EVIDENCE; reject |
| S13 | Legacy v1 receipt | Legacy shape omits dataset key and is read for historical inspection | LEGACY_UNVERIFIED; never promoted to VERIFIED |
| S14 | Dataset digest does not identify execution configuration | Keep SHA(A), change engine revision or parameters | Dataset status remains VERIFIED; execution identity remains independently distinguishable |
| S15 | Registry/artifact mismatch | Adapter and runner agree on A, registered artifact evidence binds B | MISMATCH; reject |
| S16 | No side effects on rejection | For S04-S12 and S15, compare registry/ledger/journal state before and after | No new accepted evidence or mutation beyond explicitly documented failed-run behavior |
| S17 | Synthetic purpose is explicit | Exact built-in adapter on DEVELOPMENT with default `HISTORICAL_TEST` purpose | Reject before run/usage creation |
| S18 | Synthetic cannot enter protected roles | Exact built-in adapter with `SYNTHETIC_INFRASTRUCTURE_TEST` purpose on UNTOUCHED_VALIDATION or FRESH_HOLDOUT | Reject before run/usage creation |

## 5. Cross-cutting invariants

1. Existing `input_fingerprint` meaning and composite values do not change.
2. Discovery/Stability adapter fingerprints remain composite; raw dataset SHA is a separate field.
3. Synthetic fixture digest is never substituted for dataset SHA.
4. Explicit null is valid only for the trusted synthetic mode in v2.
5. Missing field in v2 is not normalized to null.
6. Legacy v1 absence is not interpreted as explicit v2 null.
7. Runner Registry validation remains active for synthetic tests.
8. A dataset SHA match does not establish engine, parameters, fixture, strategy revision or full execution identity.
9. No gate may label NOT_APPLICABLE or LEGACY_UNVERIFIED as VERIFIED.
10. Rejected receipt evidence cannot be persisted as accepted evidence.

## 6. Implementation order after review

1. Resolve receipt schema version placement against persisted result consumers; do not invent a universal deserializer.
2. Add the independent receipt field while preserving eight-argument positional construction.
3. Add a trusted runner-side adapter classification using exact built-in synthetic type; require explicit infrastructure purpose and DEVELOPMENT role; default all other adapter types to dataset-backed.
4. Populate dataset digest only where the adapter actually reads/verifies the artifact bytes.
5. Add the focused tests above in small groups, beginning S01-S08.
6. Add runner/acceptance/provenance outcomes and legacy inspection behavior.
7. Run focused tests, full Factory suite and deterministic/forensic checks locally; record exact commands, commit, outputs and limitations.
8. Only then prepare an implementation snapshot. This specification itself does not confer canonical status.

## 7. Explicit unresolved items

- Exact location of receipt schema version and compatibility adapter for historical serialized receipts.
- Whether downstream evidence consumers require a copied dataset digest in `EvidenceBundle.result` or can bind it through a dedicated provenance result.
- Whether future synthetic adapters need a trusted registry rather than the exact built-in type exception.
- Exact acceptance policy for LEGACY_UNVERIFIED in each workflow. It must not be silently treated as dataset-verified.

No test execution is claimed by this document.
