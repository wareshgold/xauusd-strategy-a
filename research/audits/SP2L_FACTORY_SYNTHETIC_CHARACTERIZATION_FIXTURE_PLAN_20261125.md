# SP2L Factory Synthetic Characterization Fixture Plan — 2026-11-25

**Status:** DESIGN ONLY — no fixtures added or executed by this change.  
**Parent evidence:** PR #431, head `21bb5f3368eccc0aeccb2c572c4b48d8d1913744`.  
**Branch base:** `research/snapshot-line-reconciliation-20261125`.  
**Scope:** Factory provenance/route/governance characterization only; not Strategy A geometry, market behavior, execution semantics, or production readiness.

## 1. Purpose and safety boundary

This plan identifies what the existing synthetic test suite already covers, what small additional characterization fixtures could establish about current code, and what must remain blocked until explicit route-policy decisions exist.

A characterization fixture records what the inspected implementation does today. It does not approve that behavior as research policy. In particular:

- An accepted route constructor does not mean the downstream Factory implements the route.
- A non-empty Purpose accepted by the current blocklist is not an approved Purpose.
- A caller-provided `strategy_revision_frozen=True` is not a human-authorized Freeze Record.
- Different Dataset SHA values do not prove temporal independence, no partial overlap, or absence of derived-data reuse.
- A helper's existence and direct unit test do not prove that every relevant Factory call path invokes it.

All fixtures, if later implemented, must use literal synthetic bytes, isolated temporary directories, deterministic IDs/timestamps, and in-memory ledgers. They must never load local market data, MT5, Runner state, Validation data, or Fresh Holdout data.

## 2. Existing synthetic coverage inventory

| Area | Existing test(s) | Evidence in test source | Current coverage |
|---|---|---:|---|
| Validation route declaration and Handoff construction | `tests/test_validation_robustness_boundary.py` | 40-71 | Proves `HANDOFF_ROUTES` contains Validation → Robustness and Handoff construction accepts the route. Does not prove RobustnessFactory can consume it. |
| Validation dataset separation | `tests/test_validation_factory.py` | 293-303 | Accepts a distinct immutable Validation Dataset; rejects same SHA through ValidationFactory. |
| Robustness source binding | `tests/test_robustness_factory.py` | 162-191 | Accepts Stability-bound identity; rejects SHA mismatch and readiness snapshot drift. |
| Holdout role/immutability/freshness/freeze/revision | `tests/test_holdout_factory.py` | 212-280 | Covers accepted immutable Fresh Holdout, upstream SHA reuse rejection, caller Boolean false, strategy revision drift, and execution-semantics drift. |
| Purpose blocklist | `tests/test_dataset_usage.py` | 44-66, 109-121 | Rejects DEVELOPMENT/OPTIMIZATION/PARAMETER_FIT for Validation/Holdout; accepts explicit VALIDATION and FRESH_HOLDOUT_TEST examples. |
| Direct Holdout reuse helper | `tests/test_dataset_registry.py` | 45-60 | Directly calls `assert_no_holdout_reuse`; proves helper behavior only. |
| Validation-to-Development role drift | `tests/test_validation_robustness_boundary.py` | 92-125 | Covers direct registry helper and locked role identity. |
| Independent Holdout result / Forward Gate | `tests/test_forward_gate_factory.py` | 212-285, 340-468 | Covers accepted independently supplied result and multiple record/provenance/identity mismatch cases, post-Holdout tuning Boolean, and caller Freeze Boolean. |
| Full event-ledger evidence | `tests/test_forward_gate_factory.py` | 472-540 | Requires byte-level ledger evidence; rejects duplicate Holdout completions and invalid sequence without mutating the supplied snapshot. |
| Duplicate source completion | `tests/test_forward_gate_factory.py` | 543-574 | Rejects duplicate completion events without mutating the in-memory event ledger. |

This inventory is not a claim that all adjacent behaviors or every caller path are covered.

## 3. Proposed characterization fixtures

These cases may be implemented as tests only after this plan is reviewed. Expected outcomes below describe current code behavior, not policy approval.

| ID | Scenario | Existing / proposed | Expected characterization | Policy status |
|---|---|---|---|---|
| CHAR-ROUTE-01 | Validation → Robustness is declared and Handoff can be built from a synthetic Validation completion. | Existing | ACCEPT at Handoff construction. | Code behavior observed; does not approve downstream route. |
| CHAR-ROUTE-02 | Pass that Validation-origin Handoff into RobustnessFactory. | Proposed | REJECT because current RobustnessFactory requires source station `stability`. | Characterization only; route intent unresolved. |
| CHAR-PUR-01 | Validation/Holdout with DEVELOPMENT, OPTIMIZATION, or PARAMETER_FIT Purpose. | Existing | REJECT. | Current blocklist behavior; source policy does not define exhaustive allowed Purpose values. |
| CHAR-PUR-02 | Validation/Holdout with a non-empty, unrecognized Purpose label. | Proposed | Record whether current blocklist accepts it; do not interpret acceptance as authorization. | Characterization only; exact Purpose policy unresolved. |
| CHAR-HOLD-01 | Fresh Holdout has same SHA as upstream Robustness Dataset. | Existing | REJECT. | Current factory check. |
| CHAR-HOLD-02 | Fresh Holdout content is registered under another Dataset ID and the registry helper is directly called. | Existing | REJECT. | Direct helper behavior only. |
| CHAR-HOLD-03 | Same content under a different Dataset identity is supplied through a complete HoldoutFactory call path. | Proposed investigation | No expected PASS/REJECT assertion until call-path and policy coverage are approved; first record actual behavior in an isolated characterization harness. | BLOCKED for policy enforcement. |
| CHAR-TIME-01 | Dataset intervals overlap, partially overlap, touch at a boundary, or use different timezone offsets. | Deferred | No expected outcome. Capture current parser/validator behavior only if explicitly requested; do not infer interval policy. | BLOCKED — interval and timezone semantics unresolved. |
| CHAR-DERIVED-01 | Fresh Holdout is derived from, or partially contains, a prior Dataset while bytes/SHA differ. | Deferred | No expected outcome. | BLOCKED — derived-data and temporal independence policy unresolved. |
| CHAR-FREEZE-01 | Caller Boolean false versus true. | Existing | False is rejected; true is accepted as an assertion. | Characterization only; neither value proves a human-authorized Freeze Record. |
| CHAR-FORWARD-01 | Forward Gate receives a valid independently supplied Holdout result and matching complete event-ledger evidence. | Existing | ACCEPT with `production_decision=False`. | Current Gate behavior; not production authorization. |

## 4. Important test-design distinction: helper versus call path

The current registry helper `DatasetRegistry.assert_no_holdout_reuse` is directly tested in `tests/test_dataset_registry.py` lines 45-60. The inspected `HoldoutFactory.prepare_and_run` path in `src/strategy_factory/holdout_factory.py` lines 159-185 registers the supplied Holdout Dataset and invokes the runner; that inspected section does not call `assert_no_holdout_reuse`.

This observation is not, by itself, a complete proof about every possible caller in the repository. Before any enforcement change, trace all relevant call paths and establish the intended prior-use policy. Do not add a test that silently chooses a new reuse rule.

## 5. Test implementation order (if authorized)

1. Add CHAR-ROUTE-02 as a narrow characterization test using the existing synthetic Validation Handoff fixture and a complete synthetic RobustnessFactory context. It must assert only the current rejection and name the test as characterization.
2. Add CHAR-PUR-02 only as a clearly named current-blocklist characterization. It must not be named or documented as an approved Purpose.
3. For CHAR-HOLD-03, first complete a read-only call-path trace. Do not write a pass/fail test until the policy owner specifies whether same-content prior use must be rejected across role and Dataset ID changes.
4. Keep CHAR-TIME-01 and CHAR-DERIVED-01 out of executable acceptance tests until interval, timezone, overlap, and derivation semantics are explicitly resolved.
5. Preserve the existing Freeze Boolean tests but label their evidentiary limit. Do not fabricate a Freeze Record schema or signature format.

## 6. Fixture invariants

Every future fixture must satisfy all of the following:

- Uses synthetic in-memory event ledgers (`path=None`) and temporary files only.
- Uses deterministic literal payloads and SHA-256 calculated from those exact bytes.
- Does not access MT5, broker terminals, Forward Runner, Factory runtime journals, user datasets, or market-data exports.
- Does not use wall-clock time, network access, or environment-specific paths.
- Asserts no mutation of source records, event snapshots, or synthetic files on rejected paths where relevant.
- Separates current-code characterization from approved policy tests in test names, comments, and documentation.
- Does not assert statistical edge, strategy geometry, fill behavior, or production readiness.

## 7. Explicit non-goals

This plan does not define or change:

- Validation → Robustness route authorization.
- Exact Dataset equality/reuse policy for any route.
- Purpose vocabulary or station-specific Purpose allowlists.
- Freeze authority, signature, approval, or supersession.
- Fresh Holdout temporal independence, interval inclusivity, timezone, partial overlap, or derived-data rules.
- Durable registry/ledger storage, recovery, retry, or journal repair.
- SP2L geometry, P-Gap, AB=CD, fill semantics, execution rules, or BUY/SELL generation.

## 8. Exit criteria for this planning step

- Existing coverage and its limits are documented with file/line references.
- Proposed characterization cases are distinguishable from unresolved policy tests.
- No implementation or test behavior is changed by this document.
- Formal policy questions remain open and require explicit resolution before enforcement changes.

**Final status: SYNTHETIC FIXTURE DESIGN RECORDED; NO FIXTURES EXECUTED; NO POLICY CANONICALIZED; RESEARCH-ONLY.**
