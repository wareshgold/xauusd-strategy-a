# SP2L Factory Route Policy Source Audit — 2026-11-25

**Audit type:** read-only source inspection and characterization-fixture planning  
**Inspected ref:** `research/provenance-binding-v2-contract-20261124`  
**Inspected head (known branch head at audit start):** `8c5d6de2ec93513271a82ff98d63c79ea330efe5`  
**Status:** preliminary; historical snapshot reconciliation is incomplete  
**Authority:** observations below describe current source behavior only. They do not approve or canonicalize route policy.

## 1. Guardrails

- No strategy geometry, entry/exit semantics, execution rules, or production authority are defined here.
- No live/demo MT5, Forward Runner, Factory worker, actual Validation dataset, or Fresh Holdout dataset was accessed or executed.
- No test suite was run as part of this audit.
- Historical lifecycle records are not modified or repaired.
- A source-code behavior is not treated as source-confirmed research policy until reconciled with the historical source snapshots and explicit owner approval where required.

## 2. Route matrix — observed source behavior

| Route | Current source behavior observed | Audit status |
|---|---|---|
| Discovery → Stability | `HANDOFF_ROUTES` declares the route. Stability requires the source handoff's Dataset SHA and Artifact ID to equal its declared input. It also binds the Discovery Matrix JSON as a secondary input using the upstream Research Record's output artifact identity. | CODE-OBSERVED; historical policy reconciliation pending |
| Stability → Validation | Route is declared. Validation requires role `UNTOUCHED_VALIDATION`, immutable data, and a destination Dataset SHA and Artifact ID different from the upstream Stability Dataset. The Handoff itself remains bound to the upstream Stability Research Record's Dataset identity. | CODE-OBSERVED; historical policy reconciliation pending |
| Stability → Robustness | Route is declared. Robustness requires source station `stability` and exact equality of destination Dataset SHA and Artifact ID with the Stability Handoff. | CODE-OBSERVED; historical policy reconciliation pending |
| Validation → Robustness | Route is declared in `HANDOFF_ROUTES`, but `RobustnessFactory` rejects any source station other than `stability`. | SOURCE-CODE CONFLICT; keep blocked |
| Robustness → Holdout | Route is declared. Holdout requires role `FRESH_HOLDOUT`, immutable data, a Robustness source handoff, and a destination SHA and Artifact ID different from the Robustness Dataset. | CODE-OBSERVED; independence policy incomplete |
| Holdout → Forward | Prior audit indicates a Forward Gate exists and binds accepted Holdout evidence, but Freeze and independence controls still include caller assertions. This route was not re-audited line-by-line in this pass. | PRIOR AUDIT FINDING; fresh source verification pending |

**Important distinction:** the Handoff's Dataset identity describes the Dataset consumed by the upstream station. The produced output artifact is a separate identity. Neither should be substituted for the destination station's own input Dataset.

## 3. Additional controls observed

### 3.1 Dataset role and immutability

- `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT` Dataset specs require `immutable=True`.
- Dataset time bounds are currently validated by comparing `start >= end` as strings. This does not define timezone normalization, inclusive/exclusive boundaries, interval overlap, partial overlap, or derived-data leakage.
- Dataset registry identity is in-memory in the inspected implementation; durable persistence is explicitly deferred.

### 3.2 Purpose enforcement

- Usage records require a non-empty Purpose.
- For Validation and Holdout roles, the current blocklist rejects `DEVELOPMENT`, `OPTIMIZATION`, and `PARAMETER_FIT`.
- Other Purpose values are not constrained to one exact stage-specific value by this blocklist. Context defaults are not an authorization boundary because callers can override them.

### 3.3 Holdout reuse

- `DatasetRegistry.assert_no_holdout_reuse` exists and checks same content or same Dataset fingerprint under another Dataset ID when the registered record is Validation/Holdout.
- In the previously inspected Factory paths, this method was not invoked. This audit does not claim that every possible caller path was exhaustively searched.
- A different SHA alone does not establish temporal independence or absence of partial/derived overlap.

### 3.4 Freeze

- `HoldoutFactoryContext.strategy_revision_frozen` is a caller-provided Boolean with a default of `True`.
- This proves only that the caller supplied a truthy assertion. It is not a human-authorized, independently verifiable Strategy Freeze Record.

### 3.5 Lifecycle

- Handoff construction rejects a source job with both FAILED and COMPLETED terminal events.
- It rejects more than one COMPLETED event for the declared source station.
- The journal audit classifies contradictory terminal histories for manual reconciliation. Historical anomalies must remain preserved and must not be automatically repaired.
- The historical Journal path/evidence remains outside this audit; no prohibited drive or historical file was accessed.

## 4. Synthetic characterization fixtures

These fixtures characterize current code behavior only. They do not approve route semantics.

| ID | Fixture | Expected characterization |
|---|---|---|
| ROUTE-001 | Stability → Robustness; same Dataset SHA and Artifact ID | ACCEPT by current Robustness checks |
| ROUTE-002 | Stability → Robustness; changed SHA | REJECT |
| ROUTE-003 | Stability → Robustness; changed Artifact ID | REJECT |
| ROUTE-004 | Stability → Validation; immutable UNTOUCHED_VALIDATION Dataset with distinct SHA and Artifact ID | ACCEPT by current Validation checks, assuming other provenance inputs are valid |
| ROUTE-005 | Stability → Validation; destination SHA equals upstream SHA | REJECT |
| ROUTE-006 | Stability → Validation; destination Artifact ID equals upstream Artifact ID | REJECT |
| ROUTE-007 | Discovery → Stability; mismatched Discovery output artifact ID/SHA/path/size | REJECT |
| ROUTE-008 | Validation → Robustness | REJECT by current RobustnessFactory despite route declaration |
| ROUTE-009 | Holdout with non-FRESH_HOLDOUT role | REJECT |
| ROUTE-010 | Holdout with immutable=False | REJECT |
| ROUTE-011 | Holdout reuses upstream Robustness SHA or Artifact ID | REJECT |
| ROUTE-012 | Holdout Purpose is DEVELOPMENT / OPTIMIZATION / PARAMETER_FIT | REJECT at Usage Ledger |
| ROUTE-013 | Holdout Purpose is an unexpected but non-blocklisted label | Current blocklist may allow; policy requirement remains unresolved |
| ROUTE-014 | Holdout freeze Boolean is caller-supplied True without a Freeze Record | Current factory accepts this assertion; must not be treated as independently proven Freeze |
| ROUTE-015 | Dataset time ranges overlap or are adjacent at a boundary | UNRESOLVED; no approved interval semantics |
| ROUTE-016 | Holdout content is reused under another Dataset ID and the registry check is explicitly called | REJECT by registry helper |
| ROUTE-017 | Same reuse scenario through a Factory path where the helper is not called | Characterize as an enforcement gap; do not claim blocked |
| ROUTE-018 | Source lifecycle has both FAILED and COMPLETED | REJECT; manual reconciliation required |
| ROUTE-019 | More than one COMPLETED event for the same source station | REJECT; manual reconciliation required |

## 5. Blockers before policy enforcement

1. Reconcile this matrix against the historical snapshots:
   - `SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md`
   - `SP2L_FACTORY_CANDIDATE_LAB_SNAPSHOT_20261010.md`
   - `SP2L_FACTORY_FORWARD_GATE_INDEPENDENT_HOLDOUT_BINDING_20261028.md`
   - `SP2L_FACTORY_LOCAL_DATASET_OBSERVATION_CONTRACT_20261123.md`
2. Resolve whether Validation → Robustness is an intentional route, a stale declaration, or a missing implementation. Do not enable it by inference.
3. Approve exact Purpose policy per route/stage.
4. Define timestamp parsing, timezone, interval inclusivity, overlap, partial-overlap, and derived-dataset rules.
5. Replace caller-asserted Freeze with an independently verifiable human-authorized Freeze Record before any Fresh Holdout execution.
6. Establish prior-use/reuse checks and prove they are invoked on every relevant route.
7. Reconcile the historical lifecycle Journal from an explicitly permitted evidence source; do not rewrite it.

## 6. Next safe engineering step

After historical snapshot reconciliation and explicit route-policy approval, implement only the approved route-specific checks and deterministic synthetic fixtures. Run the synthetic test suite in an isolated development environment only after a read-only environment preflight. No real Validation or Fresh Holdout data should be used for these tests.
