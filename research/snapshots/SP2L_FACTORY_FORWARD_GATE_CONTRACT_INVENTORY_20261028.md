# SP2L Factory Incremental Snapshot — Forward Gate Contract Inventory — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-FORWARD-GATE-CONTRACT-INVENTORY-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Basis: `SP2L_FACTORY_HOLDOUT_DATASET_BINDING_REVIEW_20261028`
- Scope: source/API inventory and next-change plan. No runtime or trading changes.

## Existing implementation points inspected

1. `src/strategy_factory/holdout_factory.py`
   - `HoldoutFactoryResult` contains `job`, `result` (a `ResearchJobRunResult`), and the raw Holdout content SHA.
   - `ResearchJobRunResult` contains the registered/validated run identity, dataset provenance result, evidence, immutable record, snapshot, and gates.
   - `ResearchRunIdentity` contains `dataset_id`, composite `dataset_fingerprint`, and `artifact_id`.
   - `DatasetProvenanceResult` carries registered/observed composite fingerprint and registered/observed artifact IDs; raw SHA is not included as a dedicated result field.
   - The Holdout factory computes SHA from artifact bytes, validates artifact identity, registers the dataset, and passes the observed artifact to the runner.

2. `src/strategy_factory/forward_preparation.py`
   - Receives `HoldoutFactoryResult` and checks the record/job relationship, accepted result, Holdout role, manifest and strategy revision, run artifact ID, and the result's raw content SHA before it creates the Handoff and gate context.
   - It then passes only `source_record`, `source_event`, and `handoff` into `ForwardGateContext`; the completed Holdout result is not passed through the lower-level gate boundary.

3. `src/strategy_factory/forward_gate_factory.py`
   - Validates the declared record, event and handoff, but has no direct Holdout result or Registry identity input.
   - It checks that the handoff declares a valid SHA and artifact ID. The current call to `validate_evidence_bound_handoff` passes the handoff's own SHA/artifact values as expected values, so those two comparisons do not independently derive the expected values at this boundary.

4. `src/strategy_factory/forward_session_factory.py`
   - Validates the Gate result's stated evidence, route, revisions and dataset identity before freezing a demo session.
   - This is downstream validation of gate claims; it cannot independently reconstruct the original Holdout Registry state unless that state is carried across the boundary.

5. Existing synthetic gate tests are in `tests/test_forward_gate_factory.py`. They already cover frozen Holdout acceptance, wrong route, post-Holdout tuning, reused Holdout identity, unfrozen strategy, snapshot/manifest drift, malformed Forward SHA and duplicate source completion. Do not duplicate these tests.

## Contract conclusion

The strongest independent evidence is already available in `HoldoutFactoryResult.result` and its `dataset_provenance` / `run` fields. The least ambiguous next implementation is to carry that validated result into the Forward Gate boundary (or introduce a narrowly typed immutable binding derived from it), then have the gate independently cross-check:

- Holdout result is accepted and its provenance gate is PASS;
- result record equals the context's source record by run/evidence identity and fingerprint;
- result run dataset ID and composite fingerprint match the record;
- run artifact ID matches the registered/observed artifact identity;
- result raw SHA matches the observed artifact content SHA;
- handoff artifact ID and raw SHA match those independently derived values;
- source event still binds to the same run/evidence and is the unique completed Holdout event.

Do not treat a caller-created dataclass or repeated string argument as independent proof. The production path should derive the binding from the completed result object and the gate should reject a missing binding.

## Change sequence

1. Change the gate context/API with the smallest explicit completed-result binding.
2. Update all direct context constructors and call sites, preserving fail-closed behavior.
3. Add negative tests for altered raw SHA, artifact ID, dataset ID, composite fingerprint, rejected Holdout result, and record/result mismatch; assert no journal mutation.
4. Run both CI workflows and record the exact commit/results.
5. Review the resulting diff and API callers before any PR or merge decision.

## Safety

- No Strategy A geometry or execution semantics changed.
- No historical journal, live runner, MT5 state, Strategy A or Strategy B Forward Test changed.
- Synthetic tests prove contract behavior only; they do not prove broker execution or statistical edge.
- No PR was merged and no production decision was authorized.
