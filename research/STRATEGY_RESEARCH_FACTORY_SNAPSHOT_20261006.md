# SP2L Strategy Research Factory — Snapshot 2026-10-06

## Purpose

The Factory is a research and validation orchestrator. It is not a production signal generator, broker executor, or autonomous strategy selector.

## Workflow

SOURCE RESOLUTION → STRATEGY ENGINE → TEST FACTORY → OPTIMIZATION / ROBUSTNESS → UNTOUCHED VALIDATION → FRESH HOLDOUT → FORWARD VALIDATION → PRODUCTION ELIGIBILITY

A failed validation gate returns the candidate to research rather than silently changing the strategy.

## Governance rules

1. Source meaning outranks backtest performance.
2. Unresolved geometry is not silently invented by the Factory.
3. Optimizer output is a research candidate, never a canonical rule.
4. Python historical simulation and MT5 forward execution have separate roles.
5. Python ↔ MT5 reconciliation is a forward-validation gate.
6. The Factory does not generate production BUY/SELL decisions.
7. A candidate cannot become production-eligible without all required gates.
8. Live runner/config are outside this change.
9. Execution adapters and research jobs must be portable across local, VPS, CI, or cloud workers without changing declared strategy/test semantics.

## Safety

No live runner files, forward state, event logs, or production execution rules are modified by this factory foundation.

## Implemented contracts

### Strategy Lab → Compiler / Fixtures
- Manifest evidence/authority/unresolved-question models.
- Source-aligned SP2L research manifest.
- Canonical-only deterministic compiler interface.
- Deterministic synthetic fixtures with explicit BLOCKED outcomes.
- No P-Gap formula, fill semantics, SL anchor, or pending lifetime invented.

### Historical Test Engine Contract
- Explicit DEVELOPMENT / UNTOUCHED_VALIDATION / FRESH_HOLDOUT dataset roles.
- Explicit BAR_CLOSE_RESEARCH / TICK_FEASIBLE execution semantics.
- Test identity binding for strategy revision, dataset revision, range, source, parameters and objective.
- No backtest engine or strategy geometry implemented.

### Dataset Registry + Contamination Controls
- Deterministic dataset fingerprinting.
- Immutable validation/holdout controls.
- Concrete DatasetArtifact identity with SHA-256, byte-size, format and location.
- Dataset usage ledger with purpose-aware restrictions.
- Observed-vs-registered fingerprint and artifact checks.

### Research Run + Evidence Provenance
- Immutable ResearchRunIdentity and deterministic run fingerprint.
- EvidenceBundle bound to exact run provenance.
- Standalone provenance and metrics gates.
- Holdout fitting/optimization restrictions remain enforced.

### Research Metrics Contract
- Typed descriptive ResearchMetrics.
- Evidence bundles require typed metrics.
- Internal arithmetic consistency validation.
- No profitability thresholds, optimizer targets, canonical rules, or production decisions.

### Historical Execution Contract
Added:
- src/strategy_factory/execution.py
- tests/test_execution_contract.py

The execution contract binds HistoricalTestSpec, ResearchRunIdentity, ExecutionReceipt, execution semantics, strategy revision, engine revision, input fingerprint, completion state, and typed ResearchMetrics.

Gate:
- EXECUTION_CONTRACT

Boundary:
- No backtest engine.
- No proof of tick feasibility by declaration alone.
- No strategy geometry, optimization criteria, profitability thresholds, or production decisions.

### Evidence Acceptance Contract
Added:
- src/strategy_factory/acceptance.py
- tests/test_evidence_acceptance.py

The acceptance boundary requires exact agreement between HistoricalTestSpec, ResearchRunIdentity, ExecutionReceipt, EvidenceBundle, execution semantics, strategy revision, run provenance, and typed ResearchMetrics.

Gate:
- EVIDENCE_ACCEPTANCE

Acceptance behavior:
- Missing inputs → BLOCKED.
- Invalid or mismatched provenance/execution contract → FAIL.
- Invalid metrics → BLOCKED.
- Exact identity, semantics, and metrics match → PASS.

The acceptance layer does not compare performance against thresholds, define statistical significance, optimize parameters, create canonical rules, or authorize production decisions.

### Portable Historical Execution Adapter
Added:
- src/strategy_factory/adapter.py
- tests/test_execution_adapter.py

The adapter contract provides:
- a portable ExecutionAdapter protocol
- deterministic conversion of engine output into ExecutionReceipt
- exact preservation of test ID, strategy revision, and execution semantics
- explicit engine revision and input fingerprint
- rejection of incomplete execution results

The adapter is deployment-neutral: the same contract can be implemented locally, on a VPS, in CI, or on a cloud worker. It does not implement the execution engine itself.

### Portable Research Job
Added:
- src/strategy_factory/jobs.py
- tests/test_research_jobs.py

The job contract provides:
- deployment-neutral ResearchJobSpec
- deterministic SHA-256 job fingerprint
- exact strategy/test/dataset/manifest identity
- explicit execution semantics
- JSON-serializable parameters
- exact job-to-test-spec validation

A ResearchJobSpec is an input identity, not an execution command. It contains no strategy geometry, optimizer policy, or production decision logic.

## Commits

Execution:
- 0239944d
- dc75b6d9
- 12eecc06
- 656ebcda
- fde7bade

Evidence acceptance:
- 7aeb6a4b
- 41327f23
- 4592ba0b

Portable adapter:
- 863c0563
- 9b722813
- 2d257901

Portable research job:
- 47770bbd
- 93517d47
- 01950b22
