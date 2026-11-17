# SP2L Phase 0 — Factory Dependency and Boundary Audit (Static Pass) — 2026-11-17

## Status and scope

- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/architecture-consolidation-plan-20261117`
- Inspected branch tree commit: `304c47ae3c8a20f714714e519111a6d0fecfbf68`
- Scope: static inspection of Python Factory source, selected tests, and Factory launchers.
- Runtime code executed: NO
- Tests executed: NO
- MT5 / terminal / broker accessed: NO
- Live runner touched: NO
- Local dirty worktree touched: NO
- Strategy geometry / canonical rules changed: NO
- Evidence or data modified: NO

This is a source-level dependency map, not a runtime import trace or complete call graph. Import extraction was based on direct Python import statements in inspected files. Dynamic imports, runtime plugin loading, external runbooks, and local-only scripts may add dependencies not visible here. No code movement, merge, deletion, or deprecation is authorized.

## 1. Main Factory responsibility graph

The inspected source supports the following separation:

```text
ResearchJobSpec + HistoricalTestSpec + DatasetRegistry
                     |
                     v
             ResearchJobRunner
                     |
        +------------+-------------+
        |            |             |
     Adapter      Evidence     Provenance
        |            |             |
        +------------+-------------+
                     |
              ResearchRecord
                     |
             FactoryOrchestrator
                     |
          WorkerFleet + JobEventLedger
                     |
             Telemetry publisher
                     |
              StarNet adapter
                     |
              Dashboard renderer
```

Interpretation:
- `ResearchJobRunner` owns one declared job's identity, adapter execution, evidence, audit, provenance, and result gates.
- `FactoryOrchestrator` owns FIFO queueing, worker dispatch, lifecycle events, and explicit handoffs.
- `FactoryWorker` owns worker state transitions and publishes telemetry.
- `FactoryJobEventLedger` records append-only lifecycle events.
- `starnet_adapter.py` converts existing worker/event facts into renderer state.
- `telemetry.py` publishes worker status; it does not execute research.

These are separate responsibilities with direct import edges confirming the split:
- runner imports acceptance, audit, adapter, dataset/research provenance, evidence, execution, jobs, models, research record, runs, snapshot, and test contract.
- orchestrator imports jobs, job events, handoff, worker, and research record.
- worker imports telemetry.
- StarNet adapter imports job event types, not runner or strategy logic.

**Disposition: KEEP these layers separate.** There is no source evidence that Runner, Orchestrator, Worker, event ledger, telemetry, and StarNet adapter are duplicate implementations.

## 2. Factory package root exports versus module inventory

The package has 90 Python files. `src/strategy_factory/__init__.py` explicitly re-exports many public names, but does not re-export every module. Several newer service/factory modules are imported directly by their callers and tests.

This means:
- package-root exports are not a reliable complete inventory of supported services;
- removing a module because it is absent from `__init__.py` would be unsafe;
- any future public API cleanup must first classify direct imports from scripts, tests, and downstream projects.

The legacy `factory.py` is directly imported by `tests/test_strategy_factory.py`, while the newer job runner is directly imported by its own test family. The inspected source does not show the legacy facade acting as the entrypoint for the newer job runner.

## 3. Confirmed module families and dependency edges

### A. Legacy four-gate facade

Files:
- `factory.py`
- `gates.py`
- `models.py`

Direct dependency:
- `factory.py -> gates.py -> models.py`

This is a compact four-gate facade (Strategy Lab, Strategy Engine, Test Factory, Forward Validation). It is isolated from the newer `ResearchJobRunner` chain in the inspected direct imports.

Important qualification: `ResearchRun.production_eligible` currently evaluates only that exactly four gates exist and all four have status PASS. It does not itself prove canonical source authority, frozen geometry, evidence provenance, statistical validity, or any broker/execution authorization. The property name is therefore broader than the evidence it checks.

**Disposition: REVIEW / ISOLATE.** Preserve for compatibility and tests, but do not treat its boolean as production authorization. A later API/documentation change needs an explicit user-approved contract and compatibility plan.

### B. Job, run, evidence, audit, and provenance chain

Observed modules and edges:
- `jobs.py -> runs.py, test_contract.py`
- `runs.py -> datasets.py, test_contract.py, usage.py`
- `evidence.py -> metrics.py, runs.py`
- `execution.py -> metrics.py, runs.py, test_contract.py, models.py`
- `acceptance.py -> evidence.py, execution.py, models.py, provenance.py, runs.py, test_contract.py`
- `runner.py -> acceptance, audit, adapter, dataset_provenance, evidence, execution, jobs, models, research_provenance, research_record, runs, snapshot, test_contract`
- `research_record.py -> audit, evidence, research_provenance, runs, snapshot`
- `research_provenance.py -> audit, dataset_provenance, evidence, execution, jobs, runs, snapshot, test_contract`
- `audit.py -> evidence, runs, snapshot`

These modules are not interchangeable. They bind different identities and claims: dataset use, run identity, adapter execution, evidence payload, audit snapshot, and research record.

**Disposition: KEEP.** Document the contracts and exact ownership of each fingerprint before considering any consolidation.

### C. Dataset and source-resolution chain

Observed:
- `datasets.py` defines dataset artifact/identity registry and holdout-reuse checks.
- `usage.py` records dataset usage dispositions.
- `data.py` adapts historical dataset ingestion and verifies identity.
- `mt5_dataset.py` exports an MT5 M1 artifact through a subprocess.
- `source_resolution.py -> sp2l_discrimination.py`
- `source_ledger.py -> source_resolution.py`
- `source_gate.py -> source_ledger.py`
- `readiness.py -> manifest.py, source_gate.py, source_ledger.py`
- `passport_gate.py -> manifest.py, models.py, readiness.py, source_ledger.py`
- `snapshot.py -> manifest.py, models.py, passport_gate.py, readiness.py, source_ledger.py`

Dataset provenance, dataset-use governance, source-rule resolution, and source readiness are separate questions. Their shared words (source/provenance/manifest) do not prove duplication.

**Disposition: KEEP.** The MT5 exporter is operationally sensitive and BLOCKED from execution or refactor without separate approval.

### D. Validation, stability, robustness, and holdout

Observed direct dependency families:
- statistical validation: `statistics.py`, `multiple_comparison.py`, `statistical_evidence.py`, `statistical_governance.py`
- stability: `stability.py -> (standalone contract)`; `stability_evidence.py -> research_record, stability`; `stability_adapter.py -> adapter, execution, metrics, test_contract`; `stability_factory.py -> adapter, datasets, handoff, research_record, job_events, runner, jobs, snapshot, test_contract, stability_adapter`
- robustness: `robustness.py -> research_record, research_evidence_bundle, statistical_evidence, stability_evidence`; `robustness_ledger.py -> robustness`; `robustness_governance.py -> robustness, robustness_ledger, test_contract`; `robustness_factory.py -> adapter, datasets, handoff, job_events, jobs, research_record, runner, snapshot, test_contract`
- validation and holdout: `validation_factory.py` and `holdout_factory.py` each compose adapter, datasets, handoff, job events, jobs, research record, runner, snapshot, and test contract.

The Stability, Robustness, Validation, and Holdout factories share an orchestration pattern, but their test roles, evidence requirements, and handoff constraints are not automatically equivalent. They are plausible candidates for a shared internal preparation/execution helper only after field-by-field comparison.

**Disposition: REVIEW shared mechanics only.** Do not merge the factories or collapse their stage-specific contracts.

### E. Research acceptance, certification, and audit package

Observed dependency progression:
- research evidence bundle binds a research record with statistical and stability evidence.
- research evidence ledger stores bundle identities.
- research acceptance evaluates evidence bundle/ledger, research record, statistical evidence, and stability evidence.
- unified research quality composes acceptance, research evidence, comparison-validation, statistical comparison governance, and stability evidence.
- research certification consumes acceptance, evidence bundle, comparison validation, and unified quality.
- research audit package composes certification, ledgers, record, snapshot, and evidence.

These are layered assurance records, not obviously duplicate score calculations. The graph suggests an intended progression from evidence binding to acceptance, quality, certification, and audit packaging.

**Disposition: KEEP pending contract audit.** Next inspect whether each layer adds a distinct invariant or simply republishes an earlier status.

### F. Statistical comparison cluster

Observed:
- `multiple_comparison.py` provides Bonferroni/Holm p-value adjustment.
- `research_comparison.py` constructs paired comparison observations from research records/evidence.
- `statistical_comparison_evidence.py` binds comparison evidence.
- `statistical_comparison_evidence_ledger.py` records that evidence.
- `statistical_comparison_governance.py` tracks usage restrictions.
- `comparison_validation_gate.py` combines multiple-comparison results, evidence, ledger, and governance.
- `strategy_comparison.py` and `strategy_comparison_runner.py` implement a separate one-vs-one strategy comparison path.

These are related but distinct domains: within-strategy statistical validation, paired research comparisons, multiple-testing correction, and one-vs-one strategy comparisons.

**Disposition: KEEP / REVIEW naming and shared primitives.** Do not combine until the estimands, sample pairing, dataset roles, and evidence fingerprints are explicitly compared.

### G. Forward and operations boundary

The following modules form a layered forward path:
- `forward_gate_factory.py`: verifies a Fresh Holdout-to-Forward handoff and frozen identity.
- `forward_session_factory.py`: prepares a demo-forward session.
- `forward_session_lifecycle.py`: append-only in-memory session lifecycle and reconciliation receipt contract.
- `forward_runtime_bridge.py`: binds session lifecycle to injected runner/reconciliation callables.
- `forward_orchestration.py`: composes the bridge.
- `forward_observed_evidence.py`, `forward_observed_statistics.py`, and `forward_observed_report.py`: describe reconciled observations and explicitly set canonical/production eligibility false in the report.
- `forward_preparation.py`: composes holdout-to-forward preparation.
- `forward_runtime_adapter.py`: can launch an existing forward runner through subprocess.
- `mt5_reconciliation_adapter.py`: can call the existing MT5 reconciliation report builder.

The separation between proof of readiness, session lifecycle, runtime invocation, reconciliation, and observed reporting is meaningful. The runtime adapter and reconciliation adapter are not mere data models: they can invoke operational scripts.

**Disposition:**
- KEEP the pure contract/report layers.
- BLOCK execution and changes to `forward_runtime_adapter.py`, `mt5_reconciliation_adapter.py`, `mt5_dataset.py`, and `discovery_factory.py` until a separately approved Forward Ops boundary review.
- No forward runner was launched.

### H. Discovery is not purely offline

Static source inspection confirms:
- `DiscoveryFactory.prepare_and_run()` constructs `MT5M1ArtifactExporter`, exports a dataset through a subprocess, then constructs `DiscoveryMatrixAdapter` and invokes the declared discovery script.
- `DiscoveryMatrixAdapter.execute()` invokes the script through subprocess and verifies that the M1 artifact fingerprint matches the declared dataset.

This is a Factory-managed research path, but it is still an MT5 acquisition / subprocess execution boundary. The Factory label must not be mistaken for offline-safe execution.

**Disposition: BLOCK execution; preserve adapter contract.** Any future offline Discovery adapter should be a distinct injected adapter with explicit data inputs, not an implicit behavior change to the MT5-backed path.

## 4. Dashboard and StarNet launch surfaces

Static inspection confirms two independent local HTTP servers:
- `scripts/factory_dashboard.py`: default bind `127.0.0.1`, port `8788`; reads `runtime/factory_worker_status.json` or a separate demo file when `SP2L_FACTORY_DEMO=1`; imports `build_world_state`; also runs read-only Git subprocess queries for branch/head/upstream.
- `scripts/factory_starnet_world.py`: binds `127.0.0.1`, port `8789`; reads worker telemetry and job event journal; serves the StarNet frontend from `vendor/starnet-engine/frontend`; imports `FactoryJobEventLedger` and `build_world_state`.
- `scripts/factory_demo.py`: writes only `runtime/factory_demo_status.json` by default, separate from live worker status.

The two renderers are not identical implementations: one is a self-contained dashboard renderer; the other serves the external StarNet world and journal-backed handoff visualization. A unified launch command or shared read-only telemetry service may be possible, but a renderer merge is not justified by current evidence.

**Disposition:**
- KEEP both renderers for now.
- REVIEW a single documented launcher / port configuration.
- KEEP demo telemetry isolated.
- BLOCK any action that overwrites live telemetry from a demo process.
- Resolve the declared StarNet submodule/tree mismatch before relying on bootstrap.

## 5. Tests and observed coverage

The repository tree contains 65 tests whose filenames match Factory/research/forward/stability/robustness/evidence/provenance-related terms. This is a lexical candidate set, not a verified test-to-module coverage count.

Ten high-value tests were inspected for direct imports:
- `test_strategy_factory.py` tests only the legacy `factory.py` / `models.py` path.
- `test_research_job_runner.py` exercises the runner, dataset/run registries, adapter, evidence, metrics, snapshot, test contract, and usage.
- `test_factory_job_events.py` exercises the orchestrator, worker, jobs, and event ledger.
- `test_factory_handoff.py` exercises handoff, research record/provenance, and event ledger.
- `test_discovery_factory.py` exercises the Discovery factory and MT5 dataset exporter through injected test doubles.
- `test_stability_factory.py`, `test_robustness_factory.py`, `test_validation_factory.py`, and `test_holdout_factory.py` exercise their respective stage-specific factory paths.
- The tests use direct module imports rather than relying only on package-root exports.

No tests were executed. Test imports are evidence of intended dependency/contract usage, not proof that the tests currently pass.

## 6. Key findings and risks

1. **The legacy four-gate facade is separate from the newer job runner.** It should not be deleted as a duplicate; its `production_eligible` name is broader than its actual four-status check.
2. **Runner, orchestrator, worker, event ledger, telemetry, and renderer are distinct layers.** Merging them would reduce auditability.
3. **Stage factories share mechanics but not necessarily semantics.** Consider an internal helper only after proving their stage-specific invariants.
4. **“Provenance” modules protect different objects.** Dataset, research run, dashboard config, and run-config binding must remain distinct unless the fingerprint contracts are formally reconciled.
5. **Evidence modules protect different claims.** Raw execution evidence, statistical evidence, stability evidence, research bundles, comparison evidence, and certification records are not interchangeable.
6. **Discovery and Forward are not offline by default.** Their adapters can launch MT5/data/forward scripts and must remain operationally isolated.
7. **Two dashboards have different renderer responsibilities.** Unify launch ergonomics before considering renderer consolidation.
8. **No dead-code conclusion is justified yet.** A module not imported by `__init__.py` may be imported directly by a Factory, script, test, or external caller.

## 7. Provisional disposition matrix

| Component family | Disposition | Reason |
|---|---|---|
| Runner / Orchestrator / Worker / events / telemetry | KEEP separate | Different lifecycle and evidence responsibilities |
| Legacy `factory.py` / `gates.py` / `models.py` | REVIEW / ISOLATE | Separate legacy facade; misleading broad eligibility label |
| Dataset / usage / source-resolution | KEEP | Different data and source authority invariants |
| Run / execution / evidence / audit / provenance | KEEP | Distinct identity and evidence bindings |
| Stability / robustness / validation / holdout factories | REVIEW shared helper only | Similar scaffolding, distinct stage semantics |
| Statistical / multiple-comparison / certification | KEEP / REVIEW | Distinct statistical estimands and assurance layers |
| Pure forward contracts and observed reports | KEEP | Frozen identity and descriptive observation contracts |
| MT5 dataset exporter / Discovery factory | BLOCKED | Subprocess MT5 acquisition and research execution |
| Forward runtime / MT5 reconciliation adapters | BLOCKED | Can invoke existing operational scripts |
| Both dashboard renderers | KEEP | Different presentation capabilities |
| Factory demo writer | KEEP isolated | Separate demo telemetry path |
| Factory/research tests | KEEP | Direct imports prove active contract references |

## 8. Next static audit required before Phase 0 can close

1. Build the full script/test/workflow importer matrix for all 90 Factory modules, including imports outside `tests/`.
2. Compare the four stage factories field-by-field and identify only truly common mechanics.
3. Audit each evidence/provenance/statistics layer for unique invariants and fingerprint payloads.
4. Inspect the full runtime adapter command construction and all called scripts statically; classify every MT5 initialize / subprocess path.
5. Trace both dashboards' HTTP routes, telemetry reads, journal reads, and StarNet asset requirements.
6. Resolve whether any package modules are externally imported or invoked by scheduled tasks/runbooks.
7. Produce a per-module KEEP / REVIEW / BLOCKED table with importer references and test coverage before any code PR.

Phase 0 remains OPEN. Unknown importer, runtime, evidence, or external reference means BLOCKED, not safe to remove.
