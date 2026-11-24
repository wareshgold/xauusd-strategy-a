# SP2L Factory — Provenance Binding Contract v2

**Status:** DESIGN BASELINE — PARTIALLY IMPLEMENTED (Research Record v2 + Discovery output artifact lineage)  
**Date:** 2026-11-24  
**Repository baseline:** `978f56f74060938b828c08e09d9455cca6be55e0`  
**Branch:** `research/provenance-binding-v2-contract-20261124`  
**Scope:** Factory research provenance, lineage, and station-to-station binding  
**Authority:** Research software only; no canonical SP2L or production authority

---

## 1. Purpose

This contract records the proposed next-stage provenance design for the SP2L Factory. Its purpose is to make each accepted research result traceable to the exact strategy identity, dataset identity, observed local artifact, execution receipt, research record, lifecycle event, evidence artifact, and station handoff that produced it.

This is a software provenance contract. It is not a strategy specification and does not establish a statistical trading edge.

The contract is deliberately fail-closed: missing, ambiguous, contradictory, or unverifiable lineage must not be promoted as a valid research result or station handoff.

## 2. Governance and non-goals

This contract MUST NOT:

- Define or modify SP2L geometry or source meaning.
- Invent or resolve P-Gap formulas, AB=CD anchors/tolerances, fill semantics, entry/exit semantics, F10 SL anchors, F12 touch/penetration/close rules, C06 pending lifetime, or TP/execution rules.
- Select canonical parameters or declare a canonical Strategy A revision.
- Authorize production BUY/SELL decisions.
- Convert synthetic tests, software test success, or provenance validity into evidence of statistical edge.
- Automatically declare a dataset Fresh Holdout eligible or independent.
- Change MT5, any Forward Runner, or live/demo execution state.

AI may assist research, implementation, testing, source review, documentation, and analytics. Human authority remains required for strategy Freeze and all canonical or production decisions.

## 3. Source baseline and existing contracts

The following source components were inspected at baseline commit `978f56f74060938b828c08e09d9455cca6be55e0`:

- `research/contracts/SP2L_FACTORY_LOCAL_DATASET_OBSERVATION_CONTRACT_20261123.md`
- `src/strategy_factory/research_record.py`
- `src/strategy_factory/handoff.py`
- `src/strategy_factory/research_provenance.py`
- `src/strategy_factory/datasets.py`
- `src/strategy_factory/runner.py`
- `src/strategy_factory/usage.py`
- `src/strategy_factory/stability_factory.py`
- `src/strategy_factory/robustness_factory.py`
- `src/strategy_factory/validation_factory.py`
- `src/strategy_factory/holdout_factory.py`

This list is a source-review baseline, not a claim that all historical project snapshots have been fully reconciled. See Section 12.

### 3.1 Local Dataset Observation Contract

The existing contract requires every non-synthetic dataset-backed job to have:

- A registered `DatasetArtifact`.
- An Adapter exposing `dataset_artifact_path`.
- Adapter path and registered artifact location resolving to the same existing local file.
- Runner-computed SHA-256 and byte size matching declared dataset identity and registered artifact before execution.
- The same SHA-256 and byte size after execution.
- Receipt v2 or v3 `dataset_content_sha256` matching the Runner-observed digest. Receipt v3 additionally binds one typed produced local artifact.

Missing paths, non-files, path mismatches, digest mismatches, byte-size mismatches, and mutation during execution fail closed.

The exact built-in synthetic exception remains restricted to `SYNTHETIC_INFRASTRUCTURE_TEST` on `DEVELOPMENT`; its Receipt digest remains null. Synthetic fixture hashes must not be represented as real market-data observations.

**Trust limitation:** before/after file observation does not cryptographically prove that arbitrary in-process Adapter code consumed only those bytes. A malicious or faulty Adapter can read another source, misreport its behavior, or modify and restore a file between observations. Adapter implementations remain a trusted-code boundary requiring source review and controlled execution.

The current contract is local-Path-only. Remote objects, streams, and network-backed readers require a separately designed reader/snapshot contract.

### 3.2 Existing Research Record

At the inspected baseline, `ResearchRecord` contains:

- `record_revision`
- `run_id`
- `run_fingerprint`
- `evidence_id`
- `evidence_fingerprint`
- `snapshot_fingerprint`
- `audit_fingerprint`
- `strategy_id`
- `strategy_revision`
- `manifest_revision`
- `dataset_id`
- `dataset_role`
- `data_revision`
- `dataset_fingerprint`
- `execution_semantics`
- `provenance_status`
- `provenance_reasons`
- `fingerprint`

Its fingerprint uses JSON serialization with sorted keys, compact separators, and ASCII escaping. The ledger is currently in-memory and append-only within that process.

The Research Record does not currently store independent first-class fields for the observed raw content SHA-256, DatasetArtifact ID, byte size, Dataset Binding fingerprint, Receipt fingerprint, or a separate Strategy Freeze Record fingerprint.

### 3.3 Existing Handoff

At the inspected baseline, `ResearchHandoff` contains:

- `handoff_revision`
- `handoff_id`
- `job_id`
- `job_fingerprint`
- `source_station`
- `destination_station`
- `output_artifact`
- `dataset_content_sha256`
- `dataset_artifact_id`
- `source_event_fingerprint`
- `detail`
- `fingerprint`

The current declared routes are:

- Discovery → Stability
- Stability → Validation
- Stability → Robustness
- Validation → Robustness
- Robustness → Holdout
- Holdout → Forward

The current validator binds Handoff to the Research Record and source completion event, including the output artifact/evidence identity. Optional Dataset SHA and Artifact ID arguments are only checked when supplied. The inspected downstream factories perform additional checks.

### 3.4 Existing station-specific Dataset policies

A single generic rule for all Handoff routes would be incorrect.

- **Stability → Robustness:** the inspected factory requires the Robustness input SHA and Artifact ID to equal the Stability Handoff SHA and Artifact ID. This is same-dataset continuation.
- **Stability → Validation:** the inspected factory requires an immutable `UNTOUCHED_VALIDATION` dataset and rejects equality with the upstream Stability Dataset SHA or Artifact ID. This is a distinct-dataset transition.
- **Discovery → Stability:** Stability consumes an explicit Discovery Handoff and separately validates the declared Dataset artifact. Its Adapter also consumes a Discovery JSON input; that secondary input is a separate provenance concern and is not covered by the single-file observation contract.
- **Holdout and Forward:** their current contracts must be preserved and reconciled before any changes. No route policy may be generalized from the other station pairs.

The v2 design therefore requires an explicit, source-backed Dataset transition policy per route. It does not assume that every downstream station must reuse or replace the upstream Dataset.

### 3.5 Existing Freeze and readiness state

The inspected Research Record binds a Strategy ID, Strategy revision, manifest revision, and readiness snapshot fingerprint. This is useful lineage but is not, by itself, proof of a separately authorized, immutable human Strategy Freeze.

A future Freeze Record must be a distinct, human-authorized object. The implementation must not silently reinterpret an existing Boolean, readiness snapshot, or caller-supplied revision as that authority.

### 3.6 Existing registries and ledgers

The inspected Dataset Registry, Research Run Ledger, Research Record Ledger, and related usage/evidence structures include in-memory implementations. Their current process-local behavior must not be described as durable, tamper-proof, or restart-safe storage.

A durable ledger design requires a separately approved storage and root-of-trust model.

## 4. Provenance v2 entities

The following are proposed logical entities. They are not yet implemented schemas, and their exact field names/types are not frozen.

### 4.1 Strategy Freeze Record

Proposed information:

- Freeze record identity.
- Strategy ID and exact Strategy revision.
- Source commit SHA.
- Manifest identity and digest.
- Human Freeze authority.
- Freeze timestamp.
- Freeze fingerprint.
- Explicit supersession relationship, if any.

A Freeze Record must be independently retrievable and verifiable. AI must not create or approve canonical Freeze authority.

### 4.2 Dataset Binding

A Dataset Binding identifies the exact dataset artifact used by one execution.

Proposed information:

- Binding schema revision.
- Dataset ID, role, and data revision.
- DatasetArtifact ID and resolved local path identity.
- Runner-observed content SHA-256.
- Runner-observed byte size.
- Observation identity and pre/post observation results.
- Dataset fingerprint.
- Binding fingerprint.

Declared metadata and independently observed values must remain distinguishable.

Each execution must bind its own input Dataset according to its route policy. The upstream Dataset Binding and downstream Dataset Binding may be equal or different only where the source-backed route policy permits it.

### 4.3 Research Run Binding

A Run Binding links:

- Research Run ID and fingerprint.
- Job ID and fingerprint.
- Station.
- Source commit SHA.
- Strategy Freeze Record fingerprint, once such a record is approved and implemented.
- Dataset Binding fingerprint.
- Execution Receipt fingerprint.
- Execution status.

Job identity and Research Run identity must not be conflated unless existing source contracts explicitly define them as the same identifier.

### 4.4 Execution Receipt

The Receipt must be tied to the exact execution and Dataset Binding.

Required relationships:

- Receipt schema revision.
- Research Run identity.
- Dataset Binding identity.
- Runner-observed content SHA-256.
- Adapter identity and version.
- Execution outcome.
- Receipt fingerprint.

Existing Receipt v2 checks remain mandatory. Synthetic execution remains explicitly separated from real market-data execution.

### 4.5 Research Record v2

The Research Record should carry verifiable references to:

- Research Run.
- Strategy Freeze Record.
- Dataset Binding.
- DatasetArtifact.
- Execution Receipt.
- Evidence.
- Readiness snapshot and audit.
- Source lifecycle event.
- Record fingerprint.

Adding copied fields is not sufficient: every reference must be resolved and compared with its authoritative source object.

### 4.6 Produced and secondary artifacts

A produced local artifact may become a secondary input to a downstream Factory station. Its identity must not be inferred from a filename or supplied SHA alone.

The implemented bounded contract uses a typed execution output artifact containing:

- Stable artifact ID and role.
- Local path.
- Content SHA-256.
- Byte size.

The adapter declares produced artifacts and every known secondary local input in Receipt schema v3 (schema v2 remains the dataset-only receipt). Before execution, the Runner independently resolves and observes each declared secondary input; after execution it repeats the observation and rejects missing files, digest mismatches, byte-size mismatches, or changed input identity. After execution, the Runner independently resolves and observes the produced local file and rejects a missing file, digest mismatch, or byte-size mismatch. The normalized input and output observations are carried into Evidence and Research Record v2. The Record fingerprint binds all declared secondary inputs and the output artifact identity to the upstream Dataset Binding. Handoff v2 copies and validates the source output artifact ID, role, resolved path, digest, size, and output-artifact binding fingerprint against that Record; Handoff v1 remains the dataset-only legacy form.

For Discovery → Stability, the source output is the Discovery Matrix JSON. Discovery also declares the optional frozen V3 entry CSV as a secondary input. Stability requires the exact source Record and Handoff, declares the Discovery JSON as a secondary input, checks the resolved input path and byte identity before execution, and checks the same SHA and byte size again after the Stability subprocess completes. The exact observed Discovery SHA, artifact ID, and size are included in the Stability execution input fingerprint. Stability's own matrix JSON is also declared as a produced artifact for the next station.

This is local-file provenance, not cryptographic proof that arbitrary Adapter code consumed only the declared bytes. The Adapter remains a trusted-code boundary. Modify-and-restore between observations and unobserved external inputs remain limitations. Only secondary inputs explicitly declared through the adapter input-artifact contract are covered. An undeclared file or external input remains outside this observation contract and must be separately source-reviewed.

### 4.7 Lifecycle Event

A valid completion event must be bound to the same Job, Run, Research Record, station, and output artifact.

A `COMPLETED` label alone is not proof that the correct record or Dataset was used.

Duplicate or contradictory terminal histories must fail closed. Existing historical lifecycle conflicts must not be rewritten or automatically repaired.

### 4.7 Handoff v2

A Handoff must distinguish:

- The exact source Research Record.
- The source Run.
- The source completion event.
- The source Evidence/output artifact.
- The Dataset Binding used by the source execution.
- The destination station.
- The route-specific Dataset transition policy.
- The Handoff fingerprint.

The source Dataset Binding describes the input consumed by the upstream station. The output artifact describes what the upstream station produced. These are different identities and must not be substituted for each other.

The destination station must independently bind and observe its own input artifact, applying the approved route policy.

## 5. Binding invariants

The future implementation must enforce the following invariants:

1. Every dataset-backed Run has a valid Dataset Binding.
2. The Dataset Binding is derived from Runner-observed identity, not solely Adapter declarations.
3. The Receipt references the same Run and Dataset Binding.
4. Receipt SHA-256 equals the Runner-observed content SHA-256.
5. Research Record references the exact Run, Freeze, Dataset Binding, Receipt, Evidence, Snapshot, and Audit used by the execution.
6. Source completion event references the exact Job/Run/Record/station/output artifact.
7. Handoff references the exact Research Record, Run, completion event, source Dataset Binding, and output artifact.
8. Destination station applies the exact approved route-specific Dataset transition policy.
9. Destination execution creates its own Dataset Binding and Receipt.
10. Missing, ambiguous, contradictory, or unverifiable references fail closed.
11. No warning-only bypass, caller override, implicit fallback, or inferred identity is permitted.
12. Synthetic fixture provenance is never represented as real market-data provenance.

## 6. Fingerprints and canonical serialization

Existing source objects already use deterministic JSON serialization patterns, but there is not yet one approved, cross-entity canonical serialization contract for all proposed v2 objects.

Before implementation, the contract must specify:

- Exact included and excluded fields.
- Object key ordering.
- Array ordering.
- Unicode normalization/encoding behavior.
- Numeric serialization.
- Null versus missing-field semantics.
- Timestamp representation.
- Hash algorithm and digest encoding.
- Schema-version behavior.

Existing serialization behavior must be documented before any migration. New code must not silently change existing fingerprint values.

A fingerprint proves integrity of the serialized payload relative to that payload. It does not prove signer identity, authorization, source truth, or storage immutability.

## 7. Fresh Holdout and untouched Validation

Fresh Holdout and Untouched Validation are separate protected roles and must not be conflated.

A successful file hash proves byte identity at an observation point. It does not establish temporal independence, absence of partial reuse, or absence of derived-data leakage.

The future Holdout contract must separately define and verify:

- Human-authorized Strategy Freeze.
- Exact frozen Strategy revision.
- Valid upstream Handoff.
- Exact Dataset role and Purpose.
- Immutable Dataset artifact.
- Independently observed SHA-256 and byte size.
- Prior-consumption and duplicate-content checks.
- Temporal interval boundaries and overlap semantics.
- Partial overlap and derived-dataset treatment.
- Lifecycle integrity.
- Independent eligibility review.

No interval inclusivity/exclusivity, overlap threshold, or derived-data policy is invented here. These require source/owner resolution and explicit approval.

Until all required independence evidence exists, the result must remain explicitly ineligible or unverified; software PASS must not promote it to an eligible Fresh Holdout.

## 8. Purpose enforcement

Purpose must be validated against the station and Dataset role at the Factory boundary.

The implementation must first reconcile the exact existing enums, defaults, and call paths. Caller-provided defaults are not independent evidence that the requested Purpose is authorized.

No new Purpose value is introduced by this design record.

## 9. Durable provenance and recovery

A future durable provenance ledger requires:

- Stable record identities.
- Append-only semantics.
- Verifiable fingerprints.
- Explicit supersession rather than silent replacement.
- Recoverable references to source artifacts.
- Protected manifest/root-of-trust policy.
- Backup and retention policy.
- Independent audit procedure.
- Defined failure and retry semantics.

A local append-only JSONL file is not automatically tamper-proof. Hash chaining alone does not prevent replacement of the entire file and chain by an actor who controls the storage.

Failed attempts may legitimately need to remain visible. The implementation must explicitly define whether Run and Usage records created before Adapter execution represent attempted consumption, completed consumption, or another state. It must not erase evidence of failed attempts merely to make a run appear atomic.

## 10. Fail-closed gate model

Proposed logical gates:

| Gate | Required condition |
|---|---|
| `FREEZE_GATE` | Valid human-authorized Freeze Record |
| `DATASET_BINDING_GATE` | Exact Dataset and artifact identity |
| `OBSERVATION_GATE` | Independent pre/post local artifact observation |
| `RUN_BINDING_GATE` | Run, Job, Strategy, and Dataset references agree |
| `RECEIPT_GATE` | Receipt references and observed digest agree |
| `RESEARCH_RECORD_GATE` | Complete lineage references resolve |
| `LIFECYCLE_GATE` | Valid, non-conflicting lifecycle sequence |
| `HANDOFF_GATE` | Exact source Record, Event, Binding, and output artifact |
| `ROUTE_POLICY_GATE` | Destination applies the approved route-specific Dataset policy |
| `PURPOSE_GATE` | Purpose is compatible with station and Dataset role |
| `HOLDOUT_ISOLATION_GATE` | No prohibited reuse; independence evidence is sufficient |
| `DURABILITY_GATE` | Required records remain retrievable and independently verifiable |

These are design-level gate names, not implemented API names.

## 11. Synthetic acceptance matrix

Synthetic-only tests must cover at least:

- Correct complete lineage: software contract accepts.
- Wrong Dataset SHA: reject.
- Wrong DatasetArtifact ID: reject.
- Wrong byte size: reject.
- Missing or non-file artifact: reject.
- Adapter path mismatch: reject.
- Mutation during execution: reject.
- Receipt references another Dataset or Run: reject.
- Research Record references another Run, Freeze, Receipt, or Binding: reject.
- Completion Event references another Job, Run, Record, or artifact: reject.
- Handoff references another source Record, Event, Binding, or output artifact: reject.
- Invalid source/destination route: reject.
- Route-specific Dataset policy violation: reject.
- Missing or mismatched human Freeze: reject once Freeze is implemented.
- Invalid Purpose/role pairing: reject.
- Duplicate/contradictory lifecycle terminal events: reject.
- Previously consumed Holdout content: block according to the approved duplicate policy.
- Temporal independence not proven: Holdout remains unverified.
- Missing durable reference: reject.
- Fully consistent synthetic lineage: software validation passes only.

Synthetic tests validate software contracts. They do not validate strategy performance, market-data quality, canonical geometry, or statistical edge.

## 12. Historical snapshot reconciliation status

The following project snapshots are required inputs to the final source reconciliation:

- `SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md`
- `SP2L_FACTORY_CANDIDATE_LAB_SNAPSHOT_20261010.md`
- `SP2L_FACTORY_FORWARD_GATE_INDEPENDENT_HOLDOUT_BINDING_20261028.md`
- `SP2L_FACTORY_LOCAL_DATASET_OBSERVATION_CONTRACT_20261123.md`

Known constraints preserved from the available project history:

- Historical duplicate `COMPLETED` lifecycle events for `DISCOVERY-1` remain an unresolved integrity conflict.
- The historical Journal must not be truncated, rewritten, replayed, or automatically repaired.
- Dataset Observation is a software/provenance control, not evidence of a statistical edge.
- Fresh Holdout must remain independent and untouched.
- Existing Candidate Lab station boundaries must be preserved.
- Existing Forward Gate and Holdout protections must not be weakened.
- No MT5 or Forward Runner behavior is in scope.

**Reconciliation status: PARTIAL / NOT SIGNED OFF.** The historical constraints above are preserved, but the complete text of all four snapshots has not been re-read and compared line by line in this work session. No claim of complete snapshot reconciliation is made. Before implementation of Holdout, Freeze, or durable-ledger changes, each snapshot must be available and reconciled against the exact source contracts. Any discrepancy must be recorded as an explicit open item.

## 13. Source gaps to address in implementation planning

The source review at the baseline identifies the following areas for targeted engineering investigation:

1. **Partially addressed on this branch:** Research Record v2 now carries observed raw Dataset SHA, DatasetArtifact ID, byte size, Receipt fingerprint, and a Dataset Binding fingerprint. Handoff-level enforcement and migration/legacy policy remain open.
2. **Partially addressed on this branch:** for Research Record v2, Handoff construction inherits Dataset SHA and Artifact ID from the immutable Research Record, rejects conflicting caller declarations, and validates equality against the source record. Route-specific destination Dataset policy still requires a full audit.
3. Freeze authority is not represented by a separately verified human-authorized Freeze Record in the inspected Research Record model.
4. Dataset Registry and Research Record Ledger are in-memory; durability is not established.
5. **Partially addressed on this branch:** Discovery Matrix JSON is now declared as a typed produced artifact, Runner-observed after execution, recorded in Research Record v2, carried through Handoff, and checked before/after Stability. Other secondary inputs and a complete route-wide artifact policy remain open.
6. Holdout prior-use/role/purpose enforcement and temporal independence require a complete call-path audit before any code change.
7. Failure and retry semantics for Run/Usage/Lifecycle records require explicit source-level mapping.
8. Evidence integrity and duplicate/version classification must remain separate from Research Run and Dataset Binding lineage; do not duplicate or override the Evidence Integrity Monitor's responsibility.

These are engineering findings and investigation targets, not proof that real Holdout data has been contaminated.

## 14. Implementation sequence

Implementation must proceed in bounded packages:

1. Complete snapshot and source-contract reconciliation.
2. Map existing schemas, enums, route policies, and call paths into a field-level compatibility matrix.
3. Specify versioned serialization and migration behavior without changing existing fingerprints.
4. Add synthetic Dataset Binding and Research Record lineage fixtures.
5. Implement the smallest backward-compatible Research Record binding extension.
6. Implement strict Handoff-to-Record/Event/Binding reconciliation.
7. Add route-specific Dataset transition policy tests and enforcement.
8. Design and implement human-authorized Freeze Record only after its authority model is approved.
9. Complete Holdout role/Purpose/reuse/temporal-independence gates only after source and policy resolution.
10. Design durable persistence and recovery semantics separately.
11. Run focused tests, then relevant full Factory tests.
12. Perform independent source review and record immutable evidence.

No implementation step authorizes a Factory market-data run, Fresh Holdout consumption, Forward Runner, MT5, or production execution.

## 15. Explicitly unresolved decisions

The following are intentionally unresolved:

- Human Freeze authority, approval workflow, and signing mechanism.
- Cross-entity canonical serialization and migration policy.
- Logical Dataset identity versus byte-content identity.
- Secondary-input provenance contract for Discovery JSON and other Adapter inputs.
- Exact route-specific Dataset transition policy for every station pair.
- Temporal overlap, partial reuse, and derived-data independence semantics.
- Holdout eligibility authority and duplicate-content disposition.
- Durable storage, signing, root-of-trust, backup, and recovery model.
- Failed-attempt and retry lifecycle semantics.
- Relationship to existing Evidence Integrity Monitor duplicate/version decisions.
- Historical Journal provenance and the unresolved `DISCOVERY-1` lifecycle conflict.

No implementation may silently resolve these items by choosing defaults.

## 16. Acceptance criteria

This design record is ready for implementation review only when:

- All four historical snapshots have been reconciled.
- Every proposed field maps to an existing source contract or is explicitly approved as new.
- Existing route-specific Dataset semantics are preserved.
- Existing fingerprints and serialized records are not silently invalidated.
- Synthetic fixtures cover positive and negative lineage paths.
- Evidence Integrity Monitor responsibilities remain separate.
- Holdout independence is not inferred from SHA equality.
- No canonical SP2L rule, MT5 state, or Forward Runner behavior changes.
- Human approval is recorded for any new authority-bearing contract.

## 17. Implementation status at branch checkpoint

The bounded implementation packages applied on this branch are:

- `ResearchRecord` supports a versioned `RESEARCH-RECORD-2` representation.
- Dataset-backed real executions pass the Runner-observed artifact, content SHA-256, and Receipt into Research Record construction.
- Record v2 stores the DatasetArtifact ID, observed SHA-256, byte size, Receipt fingerprint, and Dataset Binding fingerprint.
- The Dataset Binding fingerprint is derived from a versioned payload containing Dataset ID, role, data revision, Dataset fingerprint, Artifact ID, content SHA-256, and byte size.
- Handoff construction for v2 records inherits the source Dataset SHA and Artifact ID and rejects any conflicting caller-supplied values; the shared validator checks these fields against the source Research Record.
- Execution Receipt schema v3 extends dataset-bound schema v2 with one typed local output artifact; schema v2 remains unchanged for dataset-only and synthetic infrastructure receipts.
- Receipt schema v3 also carries the exact typed secondary input artifact list. The Runner independently observes those files before and after execution and requires the Receipt list to match the Runner-observed pre-execution identities.
- The Runner independently observes the schema-v3 output artifact SHA-256 and byte size after execution and normalizes its resolved path before Evidence and Research Record construction.
- Research Record v2 binds declared secondary input artifacts through an input-artifact binding fingerprint and binds the produced artifact ID, role, resolved path, SHA-256, and byte size to the Dataset Binding fingerprint. Handoff v2 carries the artifact ID, role, resolved path, SHA-256, byte size, and output-artifact binding fingerprint and validates them against the source Record; Handoff v1 remains unchanged for records without a produced output artifact.
- Discovery Matrix JSON is now the explicit produced artifact for Discovery. Stability requires that exact path and identity, verifies it before execution and again after subprocess completion, and includes the observed identity in its input fingerprint. Stability Matrix JSON is declared as its own produced artifact.
- Synthetic infrastructure records without a real observed artifact remain on the legacy Research Record v1 representation; synthetic fixture hashes are not relabeled as real Dataset observations.
- Focused tests cover v2 fields, dataset and output-artifact tampering, serialization round-trip, Handoff inheritance, Discovery input drift before and during Stability execution, and output artifact observation.

**Validation state at commit `a9aea26dec1a3c6428faf26a95682bc0417df60b`:** all four remote workflows completed successfully: Factory Research Tests; Full Repository Test Suite (`911 passed in 7.24s`); Factory Journal Lock Cross-Platform Tests (Windows and Ubuntu); and SP2L forensic deterministic checks. No local test execution is claimed.

**Not yet implemented:** route-specific Dataset transition policy enforcement beyond current station checks, human-authorized Freeze Record, Holdout independence gates, bindings for secondary inputs not yet declared by the Discovery and Stability adapters, and durable ledger storage.

**Current status: PARTIAL IMPLEMENTATION. NOT CANONICAL. NOT PRODUCTION AUTHORITY.**
