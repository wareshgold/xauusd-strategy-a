# Receipt Consumer Audit Addendum — 2026-10-31

- Status: read-only source audit addendum; design only.
- Branch: `research/factory-receipt-dataset-hash-contract-20261031`
- Audited code baseline: `a39877d4f3c04e71890792995ac82ef1b76e4823`
- Scope: additional orchestration and synthetic E2E consumers inspected after the initial receipt inventory.
- No implementation or tests are included in this addendum.

## Additional confirmed consumers

| Area | Source | Finding | Consequence |
|---|---|---|---|
| Orchestrator context | `src/strategy_factory/orchestrator.py` | `RunnerExecutionContext.result_revision` defaults to `RECEIPT_METRICS_V1` and is passed through unchanged to `ResearchJobRunner.run()`. | The V2 evidence summary migration must update this default and audit callers that explicitly override it. A caller override must not permit V1 summary labeling for a V2 receipt. |
| Built-in synthetic adapter | `src/strategy_factory/synthetic.py` | Exact class is `SyntheticExecutionAdapter`; it hashes fixture/spec/engine identity into `input_fingerprint` and does not read dataset artifact bytes. | This is the exact-type non-observation exception proposed in the synthetic contract. Its V2 receipt should carry explicit null for `dataset_content_sha256`. |
| Synthetic E2E helper | `scripts/run_factory_synthetic_e2e.py` | Uses a separate `DeterministicSyntheticAdapter`, not the built-in `SyntheticExecutionAdapter`. It passes the precomputed dataset content SHA as its `input_fingerprint`, but the adapter does not read artifact bytes. | Under the exact-built-in-type trust rule, this helper is not automatically eligible for synthetic null. It must be migrated to the built-in synthetic adapter/fixture, or a separately reviewed trusted-adapter registration must be designed. It must not claim the externally computed SHA as adapter-observed bytes. |
| Dashboard | `scripts/factory_dashboard.py` | Targeted scan of the fetched dashboard source found no direct receipt/result-revision field references. | No dashboard migration is confirmed from this file; this is not proof that no other export/dashboard consumer exists. |
| Synthetic E2E test | `tests/test_factory_synthetic_e2e_run.py` | Asserts report-level `dataset_content_sha256`, accepted run and lifecycle outputs; it does not inspect receipt schema or prove adapter byte observation. | Add receipt/evidence contract assertions after the helper adapter is migrated; keep report-level dataset SHA distinct from receipt observation. |

## Orchestration migration constraint

The current default is present in both:
- `ResearchJobRunner.run(result_revision="RECEIPT_METRICS_V1")`
- `RunnerExecutionContext(result_revision="RECEIPT_METRICS_V1")`

The context passes its value directly into the runner. Implementation must define one safe compatibility rule:
- new V2 receipt summary always uses the V2 summary revision;
- an explicit incompatible V1 override must fail closed rather than silently dropping digest fields or mislabeling the summary;
- historical V1 evidence remains unchanged and readable under its old revision.

## Search coverage limitation

GitHub connector code-search calls for the simple identifiers `EvidenceBundle`, `result_revision`, `input_fingerprint`, and `ExecutionReceipt` returned zero results on the repository search surface. Because the connector search surface did not return code matches, zero results are **not** evidence of zero consumers.

The direct fetch audit in this addendum covers the named core modules, the orchestrator, the synthetic helper, and the dashboard file listed above. A complete repository-wide consumer inventory still requires a full source checkout/search or a reliable Git tree/code-search result, including:
- every direct `EvidenceBundle.result` reader;
- every `result_revision` producer/override;
- serialized evidence/receipt JSON readers and exporters;
- all external scripts and downstream integrations.

## Implementation impact

Before source changes, resolve the synthetic E2E adapter mismatch and orchestrator result-revision override behavior. Preserve the original eight positional `ExecutionReceipt` arguments and the historical `input_fingerprint` meaning. No Strategy A geometry, canonical rules, production decisions, dataset artifacts, runtime journals, or MT5 runner behavior are in scope.

No pytest/CI/runtime test was executed by this audit. No source code was changed.
