# SP2L Factory Incremental Snapshot — Handoff Duplicate-Completion Guard — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-HANDOFF-DUPLICATE-COMPLETION-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Implementation commit: `1b51f2f1d6b02bc4c153855bc100b0533cd80c60`
- Scope: fail-closed handoff guard for repeated completion events at the declared source station.

## Previous snapshots reviewed first

- `research/snapshots/SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md`
- `research/snapshots/SP2L_FACTORY_LIFECYCLE_PROVENANCE_AUDIT_20261028.md`
- `research/snapshots/SP2L_FACTORY_SEMANTIC_JOURNAL_FIXTURE_20261028.md`
- `artifacts/factory/SP2L_FACTORY_SNAPSHOT_20261007.md`

The previous semantic-journal fixture proved that an audit flags duplicate terminal history without mutation. This step closes a distinct promotion path: the handoff builder previously selected the last completed event for a source station even if that same job had multiple COMPLETED events for that station.

## Change

In `src/strategy_factory/handoff.py`, `build_research_handoff` now counts `COMPLETED` events for the requested source station and rejects more than one with `ResearchHandoffError` and a manual-reconciliation message. It does not choose the latest record or silently promote contradictory evidence.

Added `test_handoff_rejects_duplicate_completed_events_for_source_station` to `tests/test_forward_gate_factory.py`. It creates only an in-memory synthetic ledger, proves the duplicate is rejected, and confirms the ledger entries remain unchanged.

This guard is intentionally narrow. It does not require every in-memory test fixture to invent a full QUEUED/DISPATCHED history, and it does not replace the separate persisted append guard in open PR #334. That PR remains unmerged and its base SHA is stale relative to the current branch snapshot; do not blindly merge or duplicate it.

## CI on implementation commit

- Factory Research Tests — run #1096 — SUCCESS.
- SP2L forensic deterministic checks — run #639 — SUCCESS.

## Known boundaries

- Historical runtime journal remains untouched and uncorrected; the historical writer is still not conclusively identified.
- Duplicate source-station completions are now blocked at handoff promotion and covered by a synthetic test; this does not establish the provenance or validity of historical events.
- Existing Fresh Holdout → Forward E2E tests were reused, not duplicated.
- No strategy geometry, trading parameters, dataset, production gate, MT5 state, or active Forward Test was changed.
- No PR was merged and no production BUY/SELL decisions were generated.

## Next step

Inspect the remaining evidence-binding boundary between `ResearchRecord`, `ResearchHandoff`, and `ForwardGateContext` for any field whose value is only self-asserted by the handoff instead of independently checked against the completed Holdout result. Add a regression only if a concrete bypass is confirmed; do not duplicate existing manifest, snapshot fingerprint, dataset-reuse, or session-identity tests.
