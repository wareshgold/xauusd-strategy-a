# SP2L Factory Historical Snapshot Line Reconciliation — 2026-11-25

**Status:** Full-text review completed for the four named snapshots; relevant provenance, route, lifecycle, Holdout, and governance provisions reconciled against Provenance Binding Contract v2 and the inspected source files. Formal policy sign-off remains OPEN.  
**Inspected ref:** `research/route-audit-reconciliation-wording-20261125`  
**Inspected head:** `93ff9311bca8a557e4f9bb8956701f748aed2e2d`  
**Purpose:** Evidence matrix only. This document does not approve, amend, or canonicalize route policy.

## 1. Scope and guardrails

The complete text of all four named historical snapshots was retrieved and read with line numbering. Their relevant route, Dataset identity, Holdout, Freeze, Purpose, lifecycle, provenance, and operational-safety statements were compared with:

- `research/contracts/SP2L_FACTORY_PROVENANCE_BINDING_CONTRACT_V2_20261124.md`
- `research/audits/SP2L_FACTORY_ROUTE_POLICY_SOURCE_AUDIT_20261125.md`
- The current source files listed in Section 4.

This is a scoped semantic reconciliation of the full documents, not a claim that every historical local command, machine path, CI run, or operational instruction remains current. Historical statements are preserved as historical evidence and are not silently promoted to current local state.

No MT5, Forward Runner, Factory worker, market-data job, Validation dataset, or Fresh Holdout dataset was executed or accessed. No historical journal was modified. No strategy geometry, fill semantics, execution rules, canonical Strategy revision, or production authority was changed.

Source-code behavior is classified as **CODE-OBSERVED**, not source-confirmed research policy. A historical snapshot's silence is not approval. User-recorded decisions are not represented as source text. Any unresolved route remains unresolved.

## 2. Snapshot inventory and exact evidence

| ID | Snapshot and repository path | Relevant line ranges | Reconciled evidence |
|---|---|---:|---|
| S1 | `research/snapshots/SP2L_FACTORY_HANDOFF_SNAPSHOT_20261028.md` | 13-29 | Research handoff, source-first objective, governing workflow, and explicit separation between Factory research infrastructure and production signals. |
| S1 | same | 68-77 | Historical `DISCOVERY-1` duplicate COMPLETED events are a lifecycle integrity conflict; preserve original evidence; no truncate, rewrite, replay, auto-repair, or inferred trust. |
| S1 | same | 79-85 | Raw Tick Bid/Ask interval `[2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)`; Fresh Holdout boundary begins 2026-09-19 and is excluded from candidate tuning; M1 OHLC is not an exact substitute for ticks; execution/data blockers and unresolved source geometry remain open. |
| S1 | same | 98-107 | Factory-only/research-only constraints, no merge of Draft PRs without authorization, no production BUY/SELL, source meaning outranks backtest results, and AI has no canonical/production authority. |
| S2 | `artifacts/factory/SP2L_FACTORY_CANDIDATE_LAB_SNAPSHOT_20261010.md` | 44-54 | Protect untracked runtime artifacts; no cleanup/reset/overwrite; prefer small GitHub changes and user-controlled fast-forward/local validation. |
| S2 | same | 81-90 | Existing provenance gates; Holdout → Forward identity and certified SHA protections; frozen Strategy revision and post-Holdout tuning prohibition; passing tests are not statistical-edge evidence. |
| S2 | same | 103-123 | Strategy/source guardrails and the canonical research workflow, including untouched Validation, Robustness/Stability, Fresh Holdout, and production approval boundaries. |
| S2 | same | 127-148 | A real synthetic/research-only end-to-end Factory path must reflect actual persisted state; no fabricated dashboard progress or production linkage. |
| S2 | same | 154-206 | Synthetic E2E runner, isolated output paths, refusal to overwrite existing runtime artifacts, synthetic-only label, and user-requested local validation procedure. These are historical implementation/validation instructions, not evidence that a local run has since occurred. |
| S3 | `research/snapshots/SP2L_FACTORY_FORWARD_GATE_INDEPENDENT_HOLDOUT_BINDING_20261028.md` | 6-17 | Forward Gate requires an independently supplied completed Holdout result, accepted status, PASS provenance, record/job/run/dataset/artifact identity checks, raw SHA comparison, and source-event binding. |
| S3 | same | 22-25 | Negative tests cover missing/mismatched result binding, rejected Holdout, SHA/artifact/Dataset ID/fingerprint mismatches. |
| S3 | same | 34-49 | CI claims are deterministic software checks only. The historical low-level Gate limitation (one source event rather than the complete ledger) is explicitly recorded at that snapshot date; it is not a statement of current code after later changes. |
| S4 | `research/contracts/SP2L_FACTORY_LOCAL_DATASET_OBSERVATION_CONTRACT_20261123.md` | 3-19 | Local filesystem-only contract; registered DatasetArtifact; exact resolved adapter path; independent SHA-256 and byte-size observations before and after execution; Receipt v2 digest binding; fail-closed path/digest/size/mutation behavior. |
| S4 | same | 21-29 | Synthetic exception remains separate from real market-data observations; before/after hashing does not prove arbitrary Adapter code consumed only those bytes; remote/stream readers are excluded. |
| S4 | same | 31-34 | Software provenance only; no SP2L geometry, fill/execution semantics, canonical strategy, statistical edge, Holdout eligibility, production authority, MT5, or Forward Runner scope. |

## 3. Reconciliation against Provenance Binding Contract v2

| Contract section | Contract statement | Historical snapshot support / difference | Reconciliation disposition |
|---|---|---|---|
| §§1-2, lines 12-32 | Provenance software contract only; no geometry, execution, canonical parameters, production signals, or inferred Holdout eligibility. | S1 lines 19-29 and 98-107; S2 lines 103-123; S4 lines 31-34. | CONSISTENT. No strategy authority is created. |
| §3.1, lines 52-69 | Local DatasetArtifact/path binding, pre/post SHA and byte size, Receipt v2/v3, synthetic exception, Adapter trust boundary, local-only scope. | S4 lines 6-29. The historical S4 contract explicitly names Receipt v2; v3 is a later extension in Contract v2, not a historical S4 requirement. | CONSISTENT WITH VERSIONED EXTENSION. Do not rewrite the historical contract as if it specified v3. |
| §§3.3-3.4, lines 98-135 | Handoff fields and route-specific Dataset policies; one generic equality rule is incorrect; exact route policy must be source-backed. | S1 and S2 establish workflow/station boundaries but do not specify every route's exact Dataset SHA/Artifact ID comparison. S3 covers Holdout → Forward identity binding. | PARTIALLY SUPPORTED. Snapshot silence leaves exact route comparisons unresolved unless separately approved by source/owner evidence. |
| §3.5, lines 137-141 | Strategy identity/readiness snapshot is not a separately authorized human Freeze Record. | S2 lines 81-85 and 103-109 protect frozen revision/no post-Holdout tuning; none of the four snapshots defines a signed, independently verifiable Freeze Record. | CONSISTENT; HUMAN FREEZE AUTHORITY REMAINS OPEN. |
| §3.6, lines 143-147 | Registries/ledgers are in-memory; durability is not established. | S1 lines 68-77 preserves the historical journal anomaly; S2 lines 67-72 describes recovery behavior but does not approve durable root-of-trust/storage semantics. | CONSISTENT; DURABILITY/RECOVERY MODEL OPEN. |
| §4.6, lines 234-249 | Typed produced and declared secondary local artifacts; Runner observations; undeclared/external inputs remain outside trust boundary. | S4 lines 25-29 supports local-only boundary; it predates schema-v3 output/secondary-artifact additions. S2 lines 154-206 documents isolated synthetic E2E output artifacts, not a broader remote-reader contract. | CONSISTENT WITH LATER EXTENSION; no arbitrary-input coverage implied. |
| §4.7 lifecycle, lines 251-257 | Completion must bind to Job/Run/Record/station/output; contradictory terminal histories fail closed and are not repaired. | S1 lines 68-77 directly supports preservation and manual reconciliation of the historical duplicate-completion anomaly. S3 lines 43-48 says no historical journal rewrite. | CONSISTENT. |
| §7, lines 313-335 | Validation and Fresh Holdout are separate; hashes do not prove temporal independence; prior-use, overlap, partial/derived data, Freeze and eligibility need separate evidence. | S1 lines 79-85; S2 lines 81-85 and 103-123; S3 lines 43-49. None supplies approved interval inclusivity, overlap, or derived-data rules. | CONSISTENT; TEMPORAL INDEPENDENCE AND ELIGIBILITY POLICY OPEN. |
| §8, lines 337-343 | Purpose must be validated against station and Dataset role; existing enums/defaults/call paths must be reconciled; no new Purpose invented. | S1/S2 protect Holdout and Validation boundaries but do not define an exhaustive stage-specific Purpose vocabulary. | NO HISTORICAL CONFLICT; EXACT PURPOSE POLICY OPEN. |
| §9, lines 345-361 | Durable ledger, root-of-trust, backup, failure/retry semantics need separate design; hash-chain alone is not tamper-proof. | S1 lines 68-77 requires preservation of anomalous journal evidence; S2 lines 67-72 provides fail-closed recovery characterization but no full durability model. | CONSISTENT; DURABLE STORAGE AND RETRY POLICY OPEN. |
| §12, lines 411-430 | At Contract v2 drafting time, all four snapshots had not yet been reread and compared line by line; status PARTIAL / NOT SIGNED OFF. | This report now records the full-text review and scoped reconciliation performed at the inspected PR #430 head. | HISTORICAL STATUS SUPERSEDED FOR REVIEW COMPLETENESS ONLY. Formal policy sign-off remains OPEN. |
| §13, lines 432-463 | Route behavior is code observation, not approved policy; unresolved gaps include Validation → Robustness, Purpose, Freeze, Holdout reuse/temporal rules, durability, and evidence-monitor separation. | S1-S4 do not resolve those open policy questions. Current source inspection is summarized in §4 below. | CONSISTENT. Keep all listed policy blockers open unless separately resolved with evidence and approval. |

## 4. Current source inspection — behavior only

Inspected on the same PR #430 head:

| Source file | Relevant lines | Observed behavior | Classification |
|---|---:|---|---|
| `src/strategy_factory/handoff.py` | 20-26 | Declares Discovery→Stability, Stability→Validation, Stability→Robustness, Validation→Robustness, Robustness→Holdout, Holdout→Forward. | CODE-OBSERVED declaration only. |
| same | 127-178 | Handoff validation binds Job/Run/Record/source event/evidence; for Research Record v2 it checks Dataset SHA and Artifact ID against the source Record. | CODE-OBSERVED. Does not by itself approve destination transition policy. |
| `src/strategy_factory/validation_factory.py` | 71-101 | Requires immutable UNTOUCHED_VALIDATION Dataset, Stability source handoff, and destination SHA plus Artifact ID different from upstream Stability identity. | CODE-OBSERVED. Historical snapshots do not independently specify this exact comparison. |
| `src/strategy_factory/robustness_factory.py` | 95-102 | Requires destination Robustness, source station exactly Stability, and exact SHA plus Artifact ID equality with the Stability Handoff. | CODE-OBSERVED. |
| `src/strategy_factory/holdout_factory.py` | 71-83, 115-128 | Requires immutable FRESH_HOLDOUT, source station Robustness, and destination SHA/Artifact ID different from Robustness Handoff. | CODE-OBSERVED. Does not establish temporal independence. |
| same | 45-48, 75-78 | `strategy_revision_frozen` is a caller-supplied Boolean defaulting to true; false is rejected. | CODE-OBSERVED ASSERTION, NOT HUMAN FREEZE AUTHORITY. |
| `src/strategy_factory/usage.py` | 62-83 | Requires non-empty Purpose; for Validation/Holdout roles blocks DEVELOPMENT, OPTIMIZATION, PARAMETER_FIT, but does not enforce one exact stage-specific Purpose. | CODE-OBSERVED blocklist only. |
| `src/strategy_factory/datasets.py` | 136-150, 171-180 | Non-Development datasets must be immutable; helper `assert_no_holdout_reuse` checks same content/fingerprint under another Dataset ID. | CODE-OBSERVED helper. Its existence does not prove every relevant Factory call path invokes it. |
| `src/strategy_factory/forward_gate_factory.py` | 73-88, 109-167 | Requires Holdout source, FRESH_HOLDOUT record, accepted Holdout result, PASS provenance, and matching Record/Run/Job/Dataset/Artifact/SHA/source-event identities; rejects caller flag false or post-Holdout tuning true. | CODE-OBSERVED. Boolean Freeze/tuning assertions are not independently authorized evidence. |
| same | 169-227 | Requires event-ledger snapshot and byte-level evidence, validates contiguous sequence, exactly one matching Holdout completion, rejects competing Holdout failure, then validates handoff against independently supplied Holdout result. | CODE-OBSERVED later hardening beyond S3's historical one-event limitation. |
| same | 229-250 | Requires Forward Dataset ID/artifact/SHA and rejects equality of Forward Dataset ID, SHA, or Artifact ID with the Fresh Holdout identity. | CODE-OBSERVED. |
| `src/strategy_factory/forward_preparation.py` | 135-181 | Obtains event tuple, audits persisted journal snapshot when configured, compares parsed journal events to in-memory tuple, and passes SHA/size/source metadata and Holdout result to Gate. | CODE-OBSERVED. No journal repair/write is performed in this section. |

### Route-by-route disposition

| Route | Current code behavior | What the four snapshots establish | Disposition |
|---|---|---|---|
| Discovery → Stability | Route declared; Stability binds source Dataset SHA/Artifact ID and Discovery JSON secondary artifact lineage (Contract v2 §§4.6, 13). | S1-S4 do not specify exact Dataset equality or time-window/partition relationship for this route. | CODE-OBSERVED; exact route policy unresolved. |
| Stability → Validation | Immutable UNTOUCHED_VALIDATION; distinct SHA and Artifact ID from Stability. | Protected Validation boundary is supported, but exact distinctness comparison is not specified by the four snapshots. | CODE-OBSERVED; do not claim snapshot-defined equality rule. |
| Stability → Robustness | Same SHA and Artifact ID as Stability Handoff; source station must be Stability. | No snapshot states this exact equality rule. | CODE-OBSERVED; exact route policy not historically specified. |
| Validation → Robustness | Declared in global route set; RobustnessFactory rejects any source station other than Stability. | No snapshot resolves whether the route is intended, stale, or missing implementation. | DECLARED-BUT-NOT-EXECUTABLE THROUGH CURRENT ROBUSTNESS FACTORY; BLOCKED / UNRESOLVED. |
| Robustness → Holdout | Immutable FRESH_HOLDOUT; different SHA and Artifact ID from Robustness Handoff; caller Boolean for frozen revision. | S1/S2 protect Fresh Holdout boundary and prohibit tuning, but do not define temporal/partial/derived-data independence. | SNAPSHOT-SUPPORTED ROLE SEPARATION; INDEPENDENCE AND FREEZE AUTHORITY INCOMPLETE. |
| Holdout → Forward | Independent accepted Holdout result/PASS provenance/identity binding; current code additionally validates full event-ledger snapshot and distinct Forward Dataset identity. | S3 specifies independent result and identity binding; its single-event limitation is historical and later code adds ledger-wide checks. | SNAPSHOT-SUPPORTED BINDING; current code hardening observed; no production approval. |

## 5. Confirmed reconciliation discrepancy

The existing Route Policy Source Audit line 24 attributes the exact Fresh Holdout boundary date `2026-09-19` to the Candidate Lab Snapshot.

That attribution is not supported by the Candidate Lab Snapshot text reviewed here. The exact historical interval and Fresh Holdout boundary are stated in the Handoff Snapshot lines 79-85. The Candidate Lab Snapshot lines 81-85 and 103-123 supports protected Holdout/Forward identity, frozen revision/no post-Holdout tuning, and the research workflow, but does not state that exact date in the inspected text.

Disposition: correct the source attribution in the Route Policy Source Audit. This is a documentation provenance correction; it does not change the boundary date or any dataset policy.

No conflicting source statement was found in the four snapshots for the other route observations. Their silence must remain recorded as silence, not approval.

## 6. Explicitly unresolved — no canonical decision made

1. Whether Validation → Robustness is an intended route, a stale declaration, or missing implementation.
2. Exact source-backed Dataset transition policy for every station pair, including Dataset ID/role/time-window lineage.
3. Exact Purpose vocabulary and allowed Purpose per station/role.
4. Human-authorized Freeze Record, authority, signing, and supersession model.
5. Holdout prior-use enforcement and proof that checks execute on every relevant call path.
6. Timestamp parsing, timezone normalization, interval inclusivity, overlap, partial overlap, and derived-data independence.
7. Holdout eligibility authority and duplicate-content disposition.
8. Durable Dataset/Run/Record/Usage/Lifecycle persistence, root of trust, backup, recovery, failure, and retry semantics.
9. Historical `DISCOVERY-1` journal provenance and duplicate terminal-event reconciliation.
10. Relationship between Evidence Integrity Monitor duplicate/version decisions and Research Run/Dataset Binding lineage.
11. Adapter trust boundary for undeclared, indirect, or external inputs.

No item above is resolved by CI success, a passing synthetic fixture, SHA equality/inequality alone, a caller Boolean, or a dashboard state.

## 7. Review and validation status

- Four historical snapshot files: full text read; relevant provisions reconciled as recorded above.
- Provenance Binding Contract v2: relevant sections 1-17 reviewed; Section 12's earlier PARTIAL/NOT SIGNED OFF status is a historical drafting status. This report records subsequent review completion, not policy approval.
- Current source: the files and line ranges listed in Section 4 were read at the inspected PR #430 head.
- PR #430 commit `93ff9311bca8a557e4f9bb8956701f748aed2e2d`: the four associated workflows were reported completed/success by GitHub at review time. This is software CI evidence only.
- No local tests, synthetic E2E, Factory run, MT5, Runner, market-data, Validation, or Holdout execution is claimed.

**Final status: SNAPSHOT TEXT REVIEW COMPLETE; SCOPED SOURCE RECONCILIATION RECORDED; FORMAL ROUTE-POLICY SIGN-OFF OPEN; NOT CANONICAL; NOT PRODUCTION AUTHORITY.**
