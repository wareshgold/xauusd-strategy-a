# SP2L Factory Incremental Snapshot — Holdout Dataset Binding Boundary Review — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-HOLDOUT-DATASET-BINDING-REVIEW-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Scope: read-only source review; no runtime changes.

## Earlier snapshots checked

Reviewed:
- `research/snapshots/SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md`
- `research/snapshots/SP2L_FACTORY_LIFECYCLE_PROVENANCE_AUDIT_20261028.md`
- `research/snapshots/SP2L_FACTORY_SEMANTIC_JOURNAL_FIXTURE_20261028.md`
- `research/snapshots/SP2L_FACTORY_HANDOFF_DUPLICATE_COMPLETION_20261028.md`

Do not recreate the existing duplicate-completion guard or Fresh Holdout → Forward E2E coverage.

## Source facts

- `ResearchRecord` binds dataset_id, dataset role, data revision and a composite dataset_fingerprint. It does not carry raw dataset content SHA-256 or dataset artifact ID as separate fields.
- `ResearchRunIdentity` carries dataset_fingerprint and artifact_id, but not the raw content SHA-256 as a distinct field.
- `ResearchJobRunner.run` checks the observed raw content SHA against the registry and creates a validated run. The registry identity is composite metadata + content fingerprint.
- `prepare_holdout_to_forward` performs independent checks against `HoldoutFactoryResult`: supplied Holdout artifact ID must equal `result.run.artifact_id`, and supplied Holdout SHA must equal `holdout_result.holdout_dataset_content_sha256`. This is stronger than the low-level gate alone.
- `ForwardGateFactory.prepare` receives a `ForwardGateContext` containing a source record, handoff and event, but no independent dataset-registry/holdout-result object. It checks the handoff's Holdout SHA and artifact ID for shape/presence, then calls `validate_evidence_bound_handoff` with those same handoff values. That helper's optional dataset comparison is therefore self-comparison at this call site; it does not independently derive the expected raw SHA or artifact ID from the source record.
- The public lower-level gate can consequently establish internal consistency of the declared handoff, but not independently establish the raw Holdout artifact's registry binding by itself. The higher-level `prepare_holdout_to_forward` path supplies that missing check. This is an API-boundary limitation, not evidence that the higher-level preparation path is currently bypassed in production.

## Decision

Do not make a quick patch that compares raw content SHA to `ResearchRecord.dataset_fingerprint`: these are different identities. The registry fingerprint includes dataset metadata plus content fingerprint, so comparing them directly would be incorrect.

The next code change should make the low-level gate consume an explicit validated Holdout dataset identity (or the completed Holdout result/registry identity) and compare:
1. Holdout dataset_id against `ResearchRecord.dataset_id`;
2. registry composite fingerprint against `ResearchRecord.dataset_fingerprint`;
3. artifact_id and raw content SHA against the validated artifact/ingestion evidence;
4. the handoff's declared dataset identity against those independent values.

Before changing the dataclass/API, enumerate every constructor and caller and add negative tests for each mismatch. Keep the higher-level checks in `prepare_holdout_to_forward`; they are not redundant and must not be removed.

## Safety and status

- This is a bounded design finding, not a confirmed live bypass or proof of production exposure.
- No code, dataset, journal, runtime, MT5 state, or Forward Test changed in this review.
- No canonical geometry, performance claim, or production decision was made.
- No PR was merged.
