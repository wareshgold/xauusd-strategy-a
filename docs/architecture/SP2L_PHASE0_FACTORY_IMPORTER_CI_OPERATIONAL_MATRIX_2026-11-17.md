# SP2L Phase 0 — Factory Importer, Test, CI and Operational Reference Matrix (Partial Static Coverage) — 2026-11-17

## Status

- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/architecture-consolidation-plan-20261117`
- Source snapshot: `ab26ffb61f681172bd116171ac3fc977b31dcaab`
- Static source inspection only.
- No code execution, tests, MT5 initialization, broker access, runner launch, or local worktree access.
- This is a reference matrix for the inspected entrypoints and module families, not a complete 90 × 311 dependency graph. GitHub code search is default-branch scoped; it cannot establish absence of references on this non-default research branch. Dynamic imports, external callers, scheduled tasks, and local-only scripts remain outside the evidence set.

## 1. Scope counts

| Inventory | Count | Meaning |
|---|---:|---|
| Factory Python modules | 90 | All paths under `src/strategy_factory/*.py` in the inspected tree |
| Scripts | 174 | All files under `scripts/` |
| Tests | 139 | All files under `tests/` |
| Script + test source candidates | 311 | Files with Python/JS/TS/PowerShell source extensions |
| Workflows | 8 | Files under `.github/workflows/` |
| Factory/research lexical test candidates | 65 | Filename match only; not coverage proof |

## 2. Confirmed importer and test references

| Factory module / responsibility | Confirmed direct references inspected | Disposition |
|---|---|---|
| `factory.py`, `models.py` | `tests/test_strategy_factory.py` | KEEP legacy facade; REVIEW eligibility naming |
| `runner.py` | `tests/test_research_job_runner.py`, `tests/test_factory_e2e_smoke.py`, `tests/test_discovery_factory.py` | KEEP |
| `orchestrator.py`, `worker.py`, `job_events.py` | `tests/test_factory_job_events.py`, `tests/test_factory_e2e_smoke.py` | KEEP separate |
| `starnet_adapter.py` | `scripts/factory_dashboard.py`, `scripts/factory_starnet_world.py`, `tests/test_starnet_adapter.py`, `tests/test_factory_e2e_smoke.py` | KEEP presentation boundary |
| `discovery_factory.py` | `scripts/run_sp2l_factory_discovery_mt5.py`, `tests/test_discovery_factory.py` | BLOCKED operational adapter |
| `mt5_dataset.py` | `tests/test_mt5_dataset.py`, `tests/test_discovery_factory.py`; invoked by Discovery factory | BLOCKED MT5 exporter |
| `forward_runtime_adapter.py` | `tests/test_forward_runtime_adapter.py`; forward runtime bridge path | BLOCKED |
| `forward_runtime_bridge.py` | `tests/test_forward_runtime_bridge.py`, forward orchestration path | KEEP contract; runtime use BLOCKED |
| `research_acceptance.py` | `tests/test_research_acceptance.py`, certification and unified quality paths | KEEP |
| `research_evidence_bundle.py`, `research_evidence_ledger.py` | `tests/test_research_evidence_bundle.py`, `tests/test_research_evidence_ledger.py`, acceptance/certification/audit package paths | KEEP |
| `research_certification.py`, `research_certification_ledger.py` | `tests/test_research_certification.py`, `tests/test_research_certification_ledger.py`, audit package path | KEEP |
| `research_audit_package.py` | `tests/test_research_audit_package.py` | KEEP |
| `dashboard_config.py`, `dashboard_config_provenance.py` | `tests/test_dashboard_config.py`, `tests/test_dashboard_config_provenance.py` | KEEP |
| `stability_factory.py` | `tests/test_stability_factory.py` | KEEP; compare shared mechanics only |
| `robustness_factory.py` | `tests/test_robustness_factory.py` | KEEP; compare shared mechanics only |
| `validation_factory.py` | `tests/test_validation_factory.py` | KEEP; compare shared mechanics only |
| `holdout_factory.py` | `tests/test_holdout_factory.py`, `tests/test_factory_holdout_forward_e2e.py` | KEEP; compare shared mechanics only |
| `source_resolution.py`, `source_ledger.py`, `source_gate.py`, `readiness.py`, `passport_gate.py`, `snapshot.py` | Corresponding `test_source_*`, `test_readiness_snapshot.py`, `test_passport_gate.py`; downstream snapshot/readiness paths | KEEP; source authority boundary |
| `statistics.py`, `statistical_evidence.py`, `statistical_governance.py`, `multiple_comparison.py` | Corresponding `test_statistics.py`, `test_statistical_evidence.py`, `test_statistical_governance.py`, `test_multiple_comparison.py` | KEEP; distinct statistical claims |
| `comparison_validation_gate.py` | `tests/test_comparison_validation_gate.py` | KEEP |
| `stability.py`, `stability_evidence.py` | `tests/test_stability.py`, `tests/test_stability_evidence.py` | KEEP |
| `robustness.py`, `robustness_ledger.py`, `robustness_governance.py` | `tests/test_robustness.py`, `tests/test_robustness_governance.py` | KEEP |
| `mt5_reconciliation_adapter.py` | `tests/test_mt5_reconciliation_adapter.py`; adapter imports reconciliation report builder | BLOCKED operational boundary |

The rows above are confirmed examples from inspected sources. They are not an exhaustive list of every importer for each module.

## 3. Factory launcher and telemetry references

### `scripts/factory_dashboard.py`

Confirmed:
- imports `strategy_factory.starnet_adapter`;
- reads `runtime/factory_worker_status.json`;
- supports a separate `runtime/factory_demo_status.json` when `SP2L_FACTORY_DEMO=1`;
- starts a local HTTP server on `127.0.0.1:8788` by default;
- invokes Git read commands through subprocess for branch/head/upstream display.

Disposition: KEEP. Read-only presentation path, but preserve the distinction between live worker telemetry and demo telemetry.

### `scripts/factory_starnet_world.py`

Confirmed:
- imports `strategy_factory.starnet_adapter` and `strategy_factory.job_events`;
- reads worker status and job event journal;
- starts a local HTTP server on `127.0.0.1:8789`;
- serves StarNet frontend assets from `vendor/starnet-engine/frontend`.

Disposition: KEEP. Distinct renderer and event-journal visualization; not a duplicate dashboard implementation.

### `scripts/factory_demo.py`

Confirmed:
- writes demo status to `runtime/factory_demo_status.json` by default;
- accepts an explicit output path;
- does not import Factory runtime or MT5 modules in the inspected source.

Disposition: KEEP isolated. Do not point it at the live worker status file.

### Factory discovery entrypoint

`scripts/run_sp2l_factory_discovery_mt5.py` directly imports:
- dataset registry;
- Discovery factory;
- evidence ledger;
- passport gate;
- research record and run ledgers;
- readiness snapshot;
- source-resolution ledger;
- SP2L manifest builder;
- test contract;
- dataset usage ledger;
- research job runner.

It invokes the Factory Discovery path that constructs the MT5 M1 exporter. This is an operational data-acquisition workflow, not an offline-only Factory action.

Disposition: BLOCKED from execution or refactor absent explicit operational approval.

## 4. CI references

### `.github/workflows/factory-tests.yml`

Confirmed it installs pytest and executes a selected set of Factory tests, including:
- Factory E2E smoke;
- Discovery adapter / factory;
- MT5 dataset;
- handoff dataset binding;
- Stability factory;
- Validation factory.

This workflow does not demonstrate coverage of all 139 tests or all 90 Factory modules. It is a focused subset.

### `.github/workflows/research-sp2l-validation-harness.yml`

Confirmed path filters and run steps reference selected author-replica backtest and diagnostics scripts. It is not the universal Factory test gate.

### `.github/workflows/sp2l-forensic-checks.yml`

Confirmed it runs a detector-consistency script and a focused reconciliation test. It is not the full Python suite.

The other five workflows were inventoried in the previous Phase 0 report. Their write-capable behavior and branch targets remain REVIEW/BLOCKED until owner and usage are confirmed. No workflow was triggered or modified.

## 5. Operational risk classification from static inspection

| Path | Static evidence | Disposition |
|---|---|---|
| `scripts/run_sp2l_factory_discovery_mt5.py` | Factory discovery entrypoint; invokes MT5-backed dataset exporter | BLOCKED |
| `src/strategy_factory/mt5_dataset.py` | subprocess exporter contract | BLOCKED |
| `src/strategy_factory/discovery_factory.py` | orchestrates exporter and discovery script via adapter | BLOCKED |
| `src/strategy_factory/forward_runtime_adapter.py` | subprocess runner launch functions, including dry-run and production-named wrapper | BLOCKED |
| `src/strategy_factory/mt5_reconciliation_adapter.py` | imports reconciliation report builder | BLOCKED |
| `scripts/run_sp2l_v3_xauusd_forward_test.py` | imports MetaTrader5 | BLOCKED |
| `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py` | imports MetaTrader5 and calls `mt5.initialize()` | BLOCKED |
| `scripts/mt5_history_reconciliation.py` | imports MetaTrader5 and calls `mt5.initialize()` | BLOCKED |
| `scripts/export_sp2l_v3_xauusd_m1_artifact.py` | imports MetaTrader5 and initializes terminal | BLOCKED |
| `scripts/mt5_acquire_xauusd_m1.py` | imports MetaTrader5 and initializes terminal | BLOCKED |
| `scripts/forward_watchdog.py` | subprocess-spawns runner and can stop watchdog/runner | BLOCKED |
| Factory dashboards | local HTTP servers, filesystem telemetry, Git subprocess only in inspected paths | KEEP observer-only; no MT5 authority |

This is a static classification of the listed files, not a guarantee that uninspected scripts are safe. No candidate was executed.

## 6. Per-module disposition policy for the remaining Factory files

The full module tree contains 90 files. The inspected direct-reference sample does not establish a complete importer/test/CI map for every file. Therefore, for modules not explicitly listed in Section 2:

- **KEEP** when a unique source contract or stage-specific invariant is apparent, pending direct importer verification.
- **REVIEW** when names and responsibilities overlap (e.g. provenance, evidence, ledger, statistics, governance, forward preparation/runtime).
- **BLOCKED** when a module can access MT5, spawn forward/live processes, mutate operational state, or its caller chain is unresolved.
- **MERGE-CANDIDATE** is not assigned to any module yet. There is no complete evidence of equivalent inputs, outputs, invariants, importers, and tests to justify a merge.
- **RELOCATE-CANDIDATE** is not assigned yet. No path move is justified before external CLI/runbook and evidence-reference checks.

No file is classified as safe to delete or deprecate.

## 7. Gaps that keep Phase 0 open

1. The complete direct importer list for every one of the 90 Factory modules across all 174 scripts and 139 tests has not been mechanically enumerated on this non-default branch.
2. Dynamic imports, string-based module loading, console entrypoints, scheduled tasks, local-only files, and external consumers are not fully mapped.
3. All eight workflows need line-by-line command and branch-target mapping, including the five not re-opened in this pass.
4. The entire 174-script inventory needs source-level MT5 and subprocess classification, not filename heuristics.
5. Each evidence/data artifact family still needs a consumer-reference graph.
6. Factory stage factories still need a field-by-field contract comparison before extracting shared mechanics.
7. No test suite was run, so no test-pass claim is made.

## 8. Safe next step

Complete the remaining static source scans in bounded batches and publish a mechanically generated CSV/Markdown matrix with one row per Factory module and columns:
`module`, `direct_importers`, `tests`, `workflow_refs`, `dynamic_ref_risk`, `MT5_or_subprocess_boundary`, `disposition`, `evidence`.

Until that matrix is complete, Phase 0 remains OPEN and all unverified modules remain REVIEW/BLOCKED rather than removal candidates.
