# SP2L Factory Incremental Snapshot — Independent Holdout Binding — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-FORWARD-GATE-INDEPENDENT-HOLDOUT-BINDING-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Basis: `SP2L_FACTORY_FORWARD_GATE_CONTRACT_INVENTORY_20261028`
- Scope: enforce independent Holdout-result binding at the Forward Gate API boundary.
- Status: implementation and deterministic CI checks passed; not merged.

## Changes

1. `src/strategy_factory/forward_gate_factory.py`
   - Added optional `holdout_result: HoldoutFactoryResult | None` to the context for compatibility at the type boundary, but the gate fails closed when it is absent.
   - Requires the completed Holdout run to be accepted and its dataset-provenance status to be PASS.
   - Cross-checks the Holdout record, job/run IDs, dataset ID/role, composite dataset fingerprint, and registered/observed artifact IDs.
   - Independently compares the handoff raw SHA to `HoldoutFactoryResult.holdout_dataset_content_sha256`, and the handoff artifact ID to the run artifact ID.
   - Verifies the supplied source event binds to the same completed Holdout job, run fingerprint, and evidence.
   - The low-level gate no longer passes the handoff's own SHA/artifact values back as their own expected values.

2. `src/strategy_factory/forward_preparation.py`
   - Passes the actual completed `HoldoutFactoryResult` into the Forward Gate context.

3. `tests/test_forward_gate_factory.py`
   - Fixture now returns the completed result object.
   - Added negative tests for missing result binding, mismatched result record, rejected Holdout result, handoff SHA mismatch, handoff artifact mismatch, dataset ID mismatch, and composite dataset-fingerprint mismatch.
   - Existing tests continue to cover the earlier frozen-identity and routing contracts.

## Commits

- Gate binding: `a097c08ab2f6fb4cbef114fd7a2a0de2406b9728`
- Preparation wiring: `d4929ef0c6bf9e4c4b32e5ed39952e61ecf14a70`
- Initial negative tests: `35e9ca454568c61402dbc5d749770078127373cf`
- Additional provenance negative tests / CI basis: `122277cb81f4d4486ce6ed9495937acf0aa95b27`

## Verification

For commit `122277cb81f4d4486ce6ed9495937acf0aa95b27`:

- Factory Research Tests: PASS
- SP2L forensic deterministic checks: PASS

These are repository CI results for deterministic contract tests. They do not establish a statistical trading edge, broker fill behavior, or live execution safety.

## Remaining boundary

- The low-level Forward Gate receives one source event, not the full event ledger, so it cannot independently count all terminal events. The normal preparation path builds the handoff through the event ledger and the existing duplicate-completion guard. A future hardening step could carry an independently validated ledger audit/result into the gate, if needed, rather than treating one event object as proof of global uniqueness.
- The result's raw SHA and the composite dataset fingerprint are distinct identities and are not compared to each other.
- No Strategy A geometry, P-Gap formula, AB=CD interpretation, fill semantics, or execution rule was changed.
- No historical journal was rewritten; no MT5/forward-test process or state was touched.
- No PR was merged and no production decision was authorized.
