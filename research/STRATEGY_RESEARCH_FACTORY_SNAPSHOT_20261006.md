# SP2L Strategy Research Factory — Snapshot 2026-10-06

## Purpose

This snapshot freezes the first architectural foundation of the Strategy Research Factory.

The Factory is a research and validation orchestrator. It is not a production signal generator, broker executor, or autonomous strategy selector.

## Workflow

SOURCE RESOLUTION → STRATEGY ENGINE → TEST FACTORY → OPTIMIZATION / ROBUSTNESS → UNTOUCHED VALIDATION → FRESH HOLDOUT → FORWARD VALIDATION → PRODUCTION ELIGIBILITY

A failed validation gate returns the candidate to research rather than silently changing the strategy.

## Initial repository placement

- src/strategy_factory/models.py
- src/strategy_factory/gates.py
- src/strategy_factory/factory.py
- src/strategy_factory/__init__.py
- tests/test_strategy_factory.py

## Governance rules

1. Source meaning outranks backtest performance.
2. Unresolved geometry is not silently invented by the Factory.
3. Optimizer output is a research candidate, never a canonical rule.
4. Python historical simulation and MT5 forward execution have separate roles.
5. Python ↔ MT5 reconciliation is a forward-validation gate.
6. The Factory does not generate production BUY/SELL decisions.
7. A candidate cannot become production-eligible without all required gates.
8. Live forward-test runner/config are outside this change.

## Current status

- Factory foundation: IMPLEMENTED.
- Strategy compiler: NOT IMPLEMENTED.
- Canonical SP2L geometry compiler: NOT IMPLEMENTED.
- Historical test engine: NOT IMPLEMENTED.
- Optimizer: EXISTING RESEARCH TOOL, NOT YET INTEGRATED.
- Robustness engine: NOT IMPLEMENTED.
- Fresh holdout gate: NOT IMPLEMENTED.
- Forward-validation adapter: NOT IMPLEMENTED.
- Production promotion: BLOCKED BY DESIGN.

## Next planned increments

1. Define Strategy Manifest schema.
2. Build source-evidence registry and unresolved-question ledger.
3. Build deterministic strategy compiler interface.
4. Add synthetic fixtures and contract tests.
5. Build test-engine adapter around frozen event semantics.
6. Integrate optimizer as a candidate generator only.
7. Add robustness and stability gates.
8. Add untouched and fresh-holdout dataset controls.
9. Add MT5 reconciliation adapter.
10. Build a research dashboard and CLI after the engine contracts are stable.

## Branch

research/sp2l-strategy-research-factory-20261006

## Base

Created from forward-reconciliation branch head 171c1d7b687f04b0f282e8db2a0e1f53f378eaa5.

## Safety

No live runner files, forward state, event logs, or production execution rules are modified by this factory foundation.


## Increment 2026-10-06 — Strategy Lab → Compiler / Fixtures

Added:
- `src/strategy_factory/manifest.py`: evidence, authority, unresolved-question and manifest models.
- `src/strategy_factory/sp2l_manifest.py`: source-aligned SP2L research manifest.
- `src/strategy_factory/compiler.py`: canonical-only deterministic compiler interface.
- `src/strategy_factory/fixtures.py`: deterministic synthetic fixture suite.
- `tests/test_strategy_manifest.py`
- `tests/test_strategy_compiler_and_fixtures.py`

Governance:
- An unresolved/non-canonical manifest cannot compile.
- The compiler contains no SP2L geometry and does not infer missing semantics.
- Synthetic fixtures are the contract boundary before historical testing.
- Current SP2L manifest is intentionally non-canonical.

Commits:
- `abe18ca3` Strategy Manifest evidence/unresolved ledger.
- `38f1b21a` source-aligned SP2L manifest.
- `d0b8d7e0` manifest tests.
- `ed692042` canonical-only compiler interface.
- `9b6d26c6` synthetic fixture suite.
- `a27f6120` compiler/fixture tests.
- `c86f9d09` fixture accounting fix.


## Increment 2026-10-06 — SP2L Synthetic Fixtures

Added:
- `src/strategy_factory/sp2l_fixtures.py`: six source-constrained SP2L synthetic fixtures.
- `tests/test_sp2l_synthetic_fixtures.py`: deterministic fixture coverage.
- `FixtureExpectation.BLOCKED` and `FixtureBlocked` for intentionally non-executable unresolved cases.

Fixture policy:
- F13 2X midpoint is executable as a source-confirmed arithmetic contract.
- C05 M15 MA50 is represented as a source-confirmed contract.
- F12, F10, C06 and C01 executable geometry/semantics remain BLOCKED where source resolution is incomplete.
- No P-Gap formula, fill semantics, SL anchor, or pending-order lifetime was invented.
- Synthetic fixtures are not trading signals and do not generate BUY/SELL decisions.

Commits:
- `85155e70` explicit BLOCKED fixture outcome.
- `e0daf7ba` source-aligned SP2L synthetic fixtures.
- `6fbf9fdc` SP2L synthetic fixture tests.


## Increment 2026-10-06 — Historical Test Engine Contract

Added:
- `src/strategy_factory/test_contract.py`: deterministic historical-test boundary.
- `tests/test_historical_test_contract.py`: contract coverage.

Contract policy:
- Dataset roles are explicitly separated: DEVELOPMENT, UNTOUCHED_VALIDATION, FRESH_HOLDOUT.
- Untouched validation and fresh holdout datasets must be marked immutable at the contract boundary.
- Execution semantics are explicit; TICK_FEASIBLE and BAR_CLOSE_RESEARCH cannot be conflated.
- Every test identifies strategy revision, dataset revision, time range, source, execution semantics, parameters, and objective.
- The contract contains no SP2L geometry, signal generation, optimizer, or production decision logic.
- Physical/versioned holdout protection remains a later dataset-registry responsibility.

Commits:
- `f16e9aaa` historical test contract.
- `ee504bf1` historical test contract tests.


## Increment 2026-10-06 — Dataset Registry + Immutable Identity

Added:
- `src/strategy_factory/datasets.py`: deterministic dataset fingerprinting and an in-memory registry contract.
- `tests/test_dataset_registry.py`: identity, revision, immutability, holdout-isolation, and test-spec binding coverage.

Registry policy:
- Dataset identity is derived from canonical metadata plus a caller-supplied stable content fingerprint; the registry does not inspect market-data bytes itself.
- DEVELOPMENT, UNTOUCHED_VALIDATION, and FRESH_HOLDOUT remain explicit roles.
- Validation/holdout datasets must be immutable and are locked on registration.
- A registered dataset_id cannot silently change revision or content identity.
- The same dataset fingerprint cannot be registered under another dataset_id, preventing holdout reuse under a renamed identity.
- HistoricalTestSpec can be checked against the registered fingerprint before execution.
- Persistence and physical artifact locking are intentionally deferred to a later registry/storage increment.

Commits:
- `a3f94e6b` add immutable dataset registry and identity controls.
- `508131c6` make dataset fingerprint independent of registry label.
- `154adb99` / `6ee1b942` add registry tests and test-spec binding coverage.


## Increment 2026-10-06 — Concrete Dataset Artifact Identity

Added:
- `DatasetArtifact` in `src/strategy_factory/datasets.py` for a concrete stored artifact identity.
- SHA-256, byte-size, format, and location are validated as artifact metadata.
- Registered artifact identity is bound to the dataset content fingerprint and cannot be silently replaced.
- `tests/test_dataset_registry.py` now covers artifact/hash binding, mismatch rejection, locked-artifact replacement rejection, and strict artifact metadata validation.

Governance:
- The registry still does not read or mutate market-data files itself.
- The caller supplies the artifact SHA-256; the registry verifies consistency with the declared content fingerprint.
- This establishes an auditable artifact identity contract without claiming physical filesystem immutability.
- Persistent storage, artifact acquisition, and OS/object-store write protection remain future infrastructure work.

Commit:
- `29544f7c` concrete dataset artifact identity controls.
- `8917351c` artifact locking and validation tests.


## Increment 2026-10-06 — Dataset Usage Ledger + Contamination Controls

Added:
- `DatasetUsageLedger` records each accepted dataset consumption with test/strategy identity, dataset role/revision, registered vs observed fingerprint, artifact identity, purpose, and disposition.
- DEVELOPMENT datasets may be used for DEVELOPMENT purposes.
- UNTOUCHED_VALIDATION and FRESH_HOLDOUT datasets are blocked for DEVELOPMENT, OPTIMIZATION, and PARAMETER_FIT purposes.
- Observed content must match the registered dataset identity.
- When a registered artifact exists, the observed artifact must match the registered artifact exactly.
- Ledger entries are deterministic and serializable for later audit/persistence layers.

No strategy geometry, optimizer, signal generation, or production decision logic was added.


## Increment 2026-10-06 — Research Run Ledger + Evidence Provenance

Added:
- `src/strategy_factory/runs.py`: immutable research-run identity and deterministic run fingerprint.
- `src/strategy_factory/evidence.py`: evidence bundles bound to an exact research-run fingerprint.
- `src/strategy_factory/provenance.py`: standalone provenance gate.
- `tests/test_research_run_provenance.py`: run/evidence identity, contamination, artifact, and gate coverage.

Governance:
- A research result is not valid evidence without complete provenance.
- Run identity binds strategy revision, manifest revision, dataset identity/fingerprint, artifact identity, execution semantics, parameters, objective, and purpose.
- Reusing a run_id with different provenance is blocked.
- Evidence with a mismatched run fingerprint is blocked.
- Holdout datasets remain blocked for fitting/optimization through the existing usage ledger.
- Provenance is a separate gate and does not silently change production eligibility or define canonical strategy rules.
- No live runner, MT5 execution, signal generation, optimizer, or SP2L geometry was added.

Commits:
- `324a7354` research-run ledger.
- `7d43b06f` evidence bundle ledger.
- `0e217fd1` provenance gate.
- `6580d920` provenance tests.


## Increment 2026-10-06 — Research Metrics + Statistical Evidence Contract

Added:
- `src/strategy_factory/metrics.py`: typed descriptive metrics contract.
- Evidence bundles now require `ResearchMetrics`; arbitrary result payloads remain supplemental only.
- `metrics_gate` validates metric completeness and internal arithmetic consistency.
- `tests/test_research_metrics.py` plus updated provenance tests.

Metrics policy:
- The contract standardizes measurement vocabulary: trades, decisive/ambiguous counts, W/L, win rate, net R, profit factor, drawdown, gross profit/loss.
- It does not define profitability thresholds, optimization targets, canonical rules, or production decisions.
- Arithmetic consistency is enforced: totals, decisive counts, and win rate must agree.
- Profit factor may be `None` when undefined; no artificial value is invented.
- Execution semantics and full provenance remain properties of the parent Research Run.

Commits:
- `f6fe12f5` typed descriptive metrics contract.
- `8de5ba56` metrics contract tests.
- `9c4e3a60` bind EvidenceBundle to ResearchMetrics.
- `67f0dcb6` update provenance tests.
- `82a50a07` export metrics contract.
