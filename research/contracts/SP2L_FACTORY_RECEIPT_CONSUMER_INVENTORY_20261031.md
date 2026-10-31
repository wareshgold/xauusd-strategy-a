# Factory Receipt Consumer Inventory — 2026-10-31

- Audited base commit: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Design branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Scope: source/test consumer inventory supporting the Receipt Dataset Hash Contract draft.
- Status: read-only source audit; no runtime tests executed.

## Confirmed source and test consumers

| Area | Source / test | Current behavior | Change implication |
|---|---|---|---|
| Receipt model | `src/strategy_factory/execution.py` | Dataclass has 8 positional fields; `as_dict()` serializes current fields; no receipt deserializer or schema version in this module | Append any new dataclass field with a default to preserve existing positional construction; versioned serialization still needs an explicit design |
| Receipt builder | `src/strategy_factory/adapter.py` | Builder accepts and forwards `input_fingerprint`; adapter output validation checks test/strategy/semantics only | Add independent dataset digest without redefining input fingerprint; validation must include observation policy |
| Runner | `src/strategy_factory/runner.py` | Runner validates its own observed SHA before execution; receipt is validated after adapter execution; evidence result stores execution ID, engine revision, input fingerprint, semantics and metrics | Add receipt-vs-runner-observed SHA comparison for dataset-backed adapters; preserve pre-execution registry gate |
| Dataset provenance | `src/strategy_factory/dataset_provenance.py` | Compares runner-provided observed SHA to registered metadata/artifact | Keep as independent Registry-side check; do not treat it as adapter observation |
| Acceptance | `src/strategy_factory/acceptance.py` | Validates spec/run/receipt binding and evidence metrics; no adapter-observed dataset digest check | Add an independent receipt dataset binding result or consume a dedicated gate result |
| End-to-end provenance | `src/strategy_factory/research_provenance.py` | Includes DatasetProvenanceResult and validates receipt identity, but has no receipt dataset digest comparison | Extend only after the new dataset-binding status contract is defined |
| Research record | `src/strategy_factory/research_record.py` | Durable deterministic record contains dataset metadata/fingerprint and run/evidence/audit fingerprints, but does not store the ExecutionReceipt or its input fingerprint directly | Decide whether new digest belongs in record payload or is transitively bound; do not assume current record retains receipt fields |
| Discovery | `src/strategy_factory/discovery_adapter.py` | Reads M1 artifact bytes, verifies output provenance SHA, creates composite input fingerprint | Populate independent dataset digest while preserving composite input fingerprint |
| Stability | `src/strategy_factory/stability_adapter.py` | Reads artifact bytes, checks handoff SHA/artifact ID and Discovery provenance; composite input fingerprint includes dataset and output hashes | Populate independent dataset digest while preserving composite input fingerprint |
| Synthetic adapter | `src/strategy_factory/synthetic.py` | Fixture/spec/engine identity forms composite input fingerprint; does not read dataset artifact bytes | New receipt must represent non-observation explicitly, not copy the spec's Dataset Registry SHA |
| Receipt contract tests | `tests/test_execution_contract.py`, `tests/test_execution_adapter.py` | Construct receipts positionally and test validation/builder behavior | Preserve positional compatibility; add schema-v1/v2 and digest format tests |
| Synthetic tests | `tests/test_synthetic_execution.py` | Test deterministic synthetic receipt and runner end-to-end using an independently registered observed SHA | Distinguish Runner's Dataset Registry validation from Synthetic Adapter's lack of dataset-byte observation |
| Runner tests | `tests/test_research_job_runner.py` | Fake adapters currently produce receipts without dataset digest; positional receipt reconstruction exists in mismatch test | Update fake adapters and positional reconstruction deliberately; add mismatch/missing-policy cases |
| Discovery tests | `tests/test_discovery_adapter.py` | Validate output metrics and successful adapter receipt | Assert receipt dataset digest equals exact test artifact SHA |
| Synthetic E2E report | `tests/test_factory_synthetic_e2e_run.py` | Reports a dataset content SHA at script/report level | This report-level hash is not proof that SyntheticExecutionAdapter observed dataset bytes |

## Important serialization finding

The audited `ExecutionReceipt` itself has `as_dict()` but no `from_dict()` in `execution.py`. The durable `ResearchRecord` has `as_dict()/from_dict()`, but its payload does not contain the full receipt. The runner places a selected receipt summary in `EvidenceBundle.result`; this currently omits dataset content SHA and does not include the full receipt.

Therefore the v1/v2 compatibility design must inventory all persisted evidence/result consumers and any external receipt JSON before choosing where the schema version lives. Do not assume a universal receipt deserializer exists.

## Positional-constructor compatibility

Existing tests instantiate `ExecutionReceipt` positionally with eight arguments. A new optional field must be appended after existing fields with a safe default if the dataclass constructor remains positional. Every positional reconstruction site must be updated or remain compatible. A keyword-only migration may be considered only as a separately tested breaking change; it is not part of this proposal.

## Scope limits

- This inventory is source-based at the audited base commit.
- It does not prove all external consumers or downstream scripts have been found.
- No local pytest, CI, or runtime execution was performed.
- No source code, tests, dataset, receipt, journal, MT5 process, or forward runner was modified.
- No canonical Strategy A geometry or production decision rules are affected.
