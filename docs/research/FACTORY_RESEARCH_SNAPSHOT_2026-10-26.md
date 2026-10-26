# Factory Research Snapshot — 2026-10-26

## Snapshot identity

- Repository: `wareshgold/xauusd-strategy-a`
- Research branch: `research/factory-tick-gate-fixtures-20261026`
- Snapshot recorded at commit: `86d6cb95e3806c8b093d837d7f01445edeea7dd1` (pre-step baseline)
- Snapshot purpose: preserve the exact research state before the next Evidence Graph / experiment-planning increment.
- PR: [#353](https://github.com/wareshgold/xauusd-strategy-a/pull/353), OPEN, DRAFT, unmerged.
- Base branch: `research/factory-candidate-lab-20261010`
- Baseline CI: Factory Research Tests SUCCESS [run 40291596516](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40291596516); SP2L forensic deterministic checks SUCCESS [run 40291596571](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40291596571).

## Preserved work

- Tick dataset identity, timestamp duplicates/gaps, and provisional 2026-09-07 session-calendar assumption.
- Deterministic synthetic tick/order-sensitive fixtures.
- Research-only source execution preflight fixtures.
- Narrow fail-closed pending-order verification patch on this unmerged branch.
- Source-order lifecycle classification and Order/Deal/Position reconciliation fixtures.
- Lifecycle event timeline audit.
- Observed Deal economic ledger arithmetic.
- History query failure versus successful empty observation and delayed-appearance fixtures.
- Research Brain policy gate: explicit evidence roles/hashes; contradictions, failed tests, missing source evidence, and inconclusive evidence block promotion; canonical and production authorizations hard-false.

## Boundaries

- Snapshot is a GitHub research record, not a local disk/worktree archive and not a broker-account snapshot.
- No local files, local worktrees, MT5 session/account, live runner, or Strategy A forward-test artifacts were modified.
- No Strategy B run, historical replay, or performance backtest was performed.
- No PR merge or production deployment was performed.
- Synthetic CI passing does not prove live broker behavior, complete history, canonical SP2L geometry, or statistical edge.
- Replay remains blocked on unresolved execution, fill/partial-fill, cost, event ordering, trailing, 2X lifecycle, candle-construction, and immutable data-binding questions.

## Follow-up increment later on 2026-10-26

- Evidence Graph and deterministic research-action planner were added in commit 26394e883e769f7b4057c047e42bdfe048636ef3.
- Follow-up commit `0128e1f0e7d7b090d9b9921ffef3b13c34adf733` adds adversarial reconciliation fixtures for duplicate order/position identities and stricter graph role/outcome/relation validation.
- Latest verified checkpoint at snapshot refresh: `0128e1f0e7d7b090d9b9921ffef3b13c34adf733`; both focused CI workflows succeeded (runs 40293637746 and 40293637776).
- The baseline commit above remains the original snapshot point; the current branch head and its CI runs define the latest state.

## Added audit record

- `docs/research/RECONCILIATION_COUNTEREXAMPLE_AUDIT_2026-10-26.md` records the duplicate-identity counterexamples and explicitly scopes the tests as synthetic structural checks.

## Experiment ledger increment completed

- Ledger implementation: `src/strategy_factory/research_ledger.py`.
- Focused tests: `tests/test_strategy_factory_research_ledger.py`.
- Contract: `docs/research/FACTORY_RESEARCH_EXPERIMENT_LEDGER_CONTRACT_2026-10-26.md`.
- Implementation commit: `1022d1a3721a421ecaa181fdcec7abdc6fe0bf94`.
- CI workflow continuation fix: `942d0f7de494c228be444417ab4ac8b2090fb275`.
- Both workflows passed on the fixed commit: Factory Research Tests [run 40295014150](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40295014150); SP2L forensic deterministic checks [run 40295014134](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40295014134).
- The ledger does not contain fabricated historical or trading outcomes; no experiment was run as part of this increment.


## Experiment planner/registry increment — 2026-10-26

- Planner: `src/strategy_factory/experiment_planner.py`.
- Tests: `tests/test_strategy_factory_experiment_planner.py`.
- Contract: `docs/research/FACTORY_EXPERIMENT_PLANNER_REGISTRY_CONTRACT_2026-10-26.md`.
- Added stable IDs for three evidence-handling research questions and three existing synthetic test cases: same-millisecond tick order, OHLC SL/TP double-touch ambiguity, and explicit completed-bar gating. These are not hypotheses about canonical SP2L trading geometry.
- `plan_experiments` emits deterministic `PLANNED` records only, binding caller-supplied input/code hashes and the prior record hash. Unknown/duplicate IDs and dangling registry references fail closed.
- Planned records explicitly state “not executed”; no PASS/FAIL outcomes were fabricated. No actual experiment was run by this increment.
- The new planner tests are included in Factory Research Tests CI. CI must be checked on the final branch head before treating this increment as verified.
- No local files/worktrees, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No PR merge or production deployment.


## Captured execution-result ingestion increment — 2026-10-26

- Ingestion boundary: `src/strategy_factory/execution_result_ingestion.py`.
- Tests: `tests/test_strategy_factory_execution_result_ingestion.py`.
- Contract: `docs/research/FACTORY_EXECUTION_RESULT_INGESTION_CONTRACT_2026-10-26.md`.
- The boundary accepts caller-supplied run ID, command, exit code, output/environment SHA-256 hashes, evidence refs, and result summary; it creates a result record only when linked to a valid `PLANNED` record with the exact prior hash.
- Zero exit code maps to PASS and nonzero to FAIL for the captured test process only. Evidence hashes are format-validated and included in record provenance. Missing refs, invalid hashes, wrong prior hashes, or non-PLANNED source records fail closed.
- Important limitation: ingestion validates supplied metadata; it does not run the command, fetch/authenticate CI artifacts, or prove that the claimed execution occurred. Actual output bytes must be preserved and independently hashed by the caller. No captured execution report was ingested in this increment.
- New tests were added to Factory Research Tests CI; verify results on the final branch head before considering the increment checked.
- No local worktrees/files, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No historical replay, merge, or production deployment.


## Read-only pinned ledger report increment — 2026-10-26

- Report builder: `src/strategy_factory/ledger_report.py`.
- Tests: `tests/test_strategy_factory_ledger_report.py`.
- Contract: `docs/research/FACTORY_READ_ONLY_LEDGER_REPORT_CONTRACT_2026-10-26.md`.
- The report requires an externally pinned tip SHA-256 and record count, verifies the ordered chain against both, and summarizes status/evidence counts, planned/failing/inconclusive/blocked IDs, counterexample references, missing evidence, source-review-required and contradicted records.
- Wrong/missing pins, truncated chains, or invalid ledgers fail closed. Report output is read-only and deterministic; canonical/production authority remains false.
- Important limitation: the builder does not authenticate the source of external pins or captured execution artifacts. Counts are research bookkeeping, not statistical performance evidence.
- New report tests were added to Factory Research Tests CI. Verify the final branch-head runs before calling this increment validated.
- No local worktrees/files, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No replay, merge, or production deployment.


## Research Brain source-first planning increment — 2026-10-26

- Updated `src/strategy_factory/evidence_graph.py` so missing evidence roles are prioritized in the declared research order: SOURCE → DATA → TEST → EXECUTION → STATISTICAL_VALIDATION, rather than alphabetical order.
- Added `RESOLVE_SOURCE_AMBIGUITY` action for explicitly inconclusive source evidence. This requests a human-reviewed source excerpt/interpretation diff before downstream discriminating tests; it does not guess source meaning.
- Added tests proving source-first role ordering and that inconclusive source evidence does not trigger a downstream test as the first resolution step.
- This is a research-planning policy improvement, not a change to canonical SP2L geometry or production execution. All action authority flags remain false.
- CI must be checked on the latest branch head before this increment is considered validated. No local dashboard, local worktree, MT5, live runner, Strategy A forward-test, or Strategy B state was touched. StarNet visual work is intentionally deferred until the research brain policy is stable.

## Next increment

Continue strengthening the Research Brain's evidence handling and experiment prioritization against adversarial fixtures before any StarNet visual work. Keep the local dashboard deferred; do not substitute static visual mockups for working telemetry.

## Research Brain adversarial policy fixtures — 2026-10-26

- Added deterministic graph tests where multiple DATA/TEST/STATISTICAL_VALIDATION supporting records coexist with a linked SOURCE contradiction. The planner must retain a contradiction-resolution action, keep SOURCE unresolved when it has no supporting source evidence, and leave canonical/production authority false.
- Added a fail-closed case proving an INCONCLUSIVE test result cannot be attached using a SUPPORTS edge.
- Added a non-source inconclusive-result case proving a discriminating test remains proposed while missing statistical validation remains a gap; no result is presumed.
- These are synthetic policy tests only. They do not authenticate the cited source, establish the truth of a claim, execute a test, or establish statistical edge.
- No canonical geometry, live execution rule, StarNet UI, local worktree, MT5, Strategy A forward-test evidence, or Strategy B run was changed.

## Research Brain cross-evidence gate hardening — 2026-10-26

- The planner now treats a role as still unresolved when any linked evidence for that role contradicts the claim, even if another linked item of the same role supports it. A contradiction can no longer be masked by a same-role supporting record.
- Canonical-rule-change claims now always retain a separate HUMAN_SOURCE_REVIEW action, even when missing evidence or contradiction-resolution actions are also present.
- Added adversarial tests for mixed SOURCE support/contradiction and for retaining human review alongside other open research actions.
- This is planner policy only. It does not adjudicate which source excerpt is correct, decide canonical geometry, execute experiments, or authorize production decisions. Both authority flags remain false.

## Statistical comparison purpose allowlist hardening — 2026-10-26

- Updated `src/strategy_factory/statistical_comparison_governance.py` to fail closed unless usage purpose is one of `FINAL_EVIDENCE`, `DEVELOPMENT`, `OPTIMIZATION`, or `PARAMETER_FIT`. Unknown aliases and empty values cannot be recorded as allowed usage.
- Added negative tests for empty, misspelled, unknown, and holdout-specific unknown purposes; tests assert the usage ledger remains unchanged after rejection.
- This closes a purpose-label bypass at the usage-ledger boundary; it does not authenticate the dataset role or source of the evidence, and it does not establish statistical significance or authorize production.
- CI status must be checked on the final commit before treating this increment as verified. No local worktrees/files, MT5, forward runners, Strategy A or Strategy B execution, PR merge, or production deployment were performed.

## Dataset-role provenance boundary audit — 2026-10-26

- Inspected `ResearchRecord`, `ResearchEvidenceBundle`, `ResearchComparison`, `StatisticalComparisonEvidence`, the comparison evidence ledger, and the unified comparison validation gate.
- The upstream `ResearchRecord` does carry `dataset_id`, `dataset_role`, `data_revision`, and `dataset_fingerprint`; its accepted provenance status is required to be PASS. The research evidence bundle also binds dataset ID and role to that record.
- Boundary limitation found: `ResearchComparison` reduces each observation to run ID, research-record fingerprint, bundle fingerprint, and metrics. Its top-level `dataset_role` is then fingerprinted as a comparison field, but the comparison validation gate does not receive the underlying ResearchRecord or ResearchEvidenceBundle registry to independently resolve the record fingerprint and verify that the declared role is the role recorded upstream. Statistical-comparison evidence consequently binds the comparison's declared role, not an independently re-resolved dataset attestation.
- Therefore a valid hash proves internal consistency of the submitted comparison object, not truth of the claimed dataset role. This is an unresolved provenance gap, not evidence that a real production path has exploited it.
- Do not treat `FRESH_HOLDOUT` as independently authenticated through this gate alone. The next implementation step should add a trusted, append-only source-record/role attestation lookup (keyed by exact research-record fingerprint and dataset fingerprint), and require the comparison gate to validate every baseline/candidate observation against it before governance can PASS. Add adversarial tests for relabeling DEVELOPMENT as FRESH_HOLDOUT and for mismatched dataset IDs/fingerprints.
- No canonical SP2L rules, execution behavior, live runners, Strategy A/Strategy B, local worktrees, or production authorization were changed. The prior allowlist hardening remains CI-verified; this audit finding itself is documentation only and does not claim to close the role-authentication gap.

## Comparison holdout-role provenance gate — 2026-10-26

- Updated `evaluate_comparison_validation_gate` so comparisons labelled `UNTOUCHED_VALIDATION` or `FRESH_HOLDOUT` require a supplied `ResearchRecordLedger`.
- The gate resolves every baseline/candidate by `run_id`, validates the record fingerprint, and checks that the record's dataset role matches the comparison role and that dataset ID/fingerprint are present. Unresolved or mismatched records block governance; governance is not recorded after a provenance block.
- Added adversarial tests for a re-fingerprinted DEVELOPMENT comparison relabelled as FRESH_HOLDOUT and for an empty record ledger. Both must remain BLOCKED.
- Scope limitation: `ResearchRecordLedger` is currently an in-memory application ledger, not an independently authenticated, durable dataset attestation service. This change prevents the comparison gate from treating a self-declared holdout role as sufficient, but does not establish external immutability/authenticity of the ledger or underlying data. A durable, independently pinned dataset manifest and trusted registry remain necessary before treating holdout provenance as fully authenticated.
- The gate's existing DEVELOPMENT comparison behavior is unchanged. This is a governance/provenance hardening step, not statistical evidence of edge and not canonical SP2L rule approval.
- No local worktrees/files, MT5, Strategy A/Strategy B forward runners, PR merge, or production deployment were touched.

## Externally pinned dataset-manifest boundary — 2026-10-26

- Added `src/strategy_factory/dataset_manifest.py`: deterministic content-addressed dataset manifests and an append-only registry that accepts a manifest only when its fingerprint matches a separately supplied trusted pin.
- Holdout comparison validation now requires both the research-record ledger and the dataset-manifest registry for `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT`. It checks role, dataset fingerprint, revision, and immutability against the pinned manifest before governance can be recorded.
- Added `tests/test_dataset_manifest.py` for deterministic fingerprints, missing/wrong pins, tampering, role/dataset/revision mismatch, and immutable registration.
- Trust limitation is explicit: a SHA-256 digest provides integrity, not publisher authenticity. The trusted pin must come from a separately controlled source (for example, a protected registry or reviewed release artifact); a caller-supplied untrusted pin does not establish trust. The registry itself is currently in-memory and is not claimed to be durable storage.
- This is a dataset-provenance/governance boundary only. It does not resolve SP2L geometry, establish statistical edge, or authorize canonical/production decisions. CI must pass on the final branch head before this increment is treated as validated.
- No local worktrees/files, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No merge or production deployment.

