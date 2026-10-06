# SP2L Strategy Research Factory — Snapshot 2026-10-06

## Purpose

The Factory is a research and validation orchestrator. It is not a production signal generator, broker executor, or autonomous strategy selector.

## Workflow

SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → STRATEGY ENGINE → TEST FACTORY → OPTIMIZATION / ROBUSTNESS → UNTOUCHED VALIDATION → FRESH HOLDOUT → FORWARD VALIDATION → PRODUCTION ELIGIBILITY

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
10. New infrastructure must prove determinism and provenance before real historical execution is introduced.

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

## Current verification status

Factory contract suite:
- 89 tests passed
- ResearchJobSpec tests: 10 passed
- Full Factory suite: 89 passed

The following layer is considered stable enough to build on, but remains research-only. Existing contracts should not be weakened merely to accommodate future engine behavior.

## Roadmap — path forward

### Phase 1 — Complete the orchestration boundary
Status: NEXT

1. Research Job Runner contract.
2. Validate job against registered dataset/test identity.
3. Create or bind ResearchRunIdentity.
4. Resolve an ExecutionAdapter.
5. Execute exactly once under the declared semantics.
6. Produce ExecutionReceipt.
7. Produce EvidenceBundle only from the receipt.
8. Run provenance/execution/metrics/evidence-acceptance gates.
9. Return a deterministic run result.
10. Add tests for missing, mismatched, duplicate, incomplete, and successful jobs.

Important:
- Runner is orchestration only.
- It must not know SP2L geometry.
- It must not generate BUY/SELL decisions.
- It must not optimize parameters.

### Phase 2 — Synthetic end-to-end execution
Status: AFTER PHASE 1

Build a small deterministic synthetic execution adapter/engine whose inputs and expected outputs are completely controlled by fixtures.

Purpose:
- prove Job → Run → Adapter → Receipt → Evidence end-to-end;
- prove deterministic fingerprints;
- prove repeatability across processes/environments;
- exercise BAR_CLOSE_RESEARCH and TICK_FEASIBLE as separate declared semantics;
- verify failure isolation.

This phase is infrastructure validation, not Strategy A validation.

### Phase 3 — Historical data adapter / dataset ingestion
Status: PLANNED

Create a deployment-neutral historical-data boundary.

Requirements:
- registered dataset identity;
- artifact SHA-256;
- exact time range;
- source metadata;
- deterministic loading;
- no silent resampling;
- no hidden timezone conversion;
- no accidental holdout access;
- reproducible input fingerprint.

The data layer must not define strategy geometry.

### Phase 4 — Generic deterministic historical execution kernel
Status: PLANNED

Build the execution kernel independently from SP2L-specific signal geometry.

The kernel will eventually handle explicitly declared mechanics such as:
- chronological event processing;
- entry/exit event ordering;
- SL/TP evaluation;
- position lifecycle;
- ambiguous-bar handling;
- deterministic accounting;
- execution semantics;
- traceable trade-level evidence.

BAR_CLOSE_RESEARCH and TICK_FEASIBLE must remain distinct. A model cannot claim tick feasibility merely because it was run on M1 bars.

### Phase 5 — SP2L Strategy Engine
Status: BLOCKED BY SOURCE RESOLUTION / FROZEN GEOMETRY

Only after canonical source resolution and frozen geometry.

Required before canonical implementation:
- P-Gap executable definition;
- F12 retrace trigger semantics;
- exact executable entry/fill semantics;
- F10 exact SL anchor;
- C06 pending lifetime semantics;
- any other unresolved geometry required by the source.

Until then, SP2L-specific execution remains research/diagnostic only and cannot be promoted to canonical.

### Phase 6 — Test Factory
Status: PLANNED AFTER ENGINE + FROZEN GEOMETRY

Build standardized experiment generation and execution.

It must:
- create explicit TestSpecs;
- bind exact strategy revision;
- bind exact dataset revision;
- preserve DEVELOPMENT / UNTOUCHED_VALIDATION / FRESH_HOLDOUT separation;
- record every parameter;
- generate auditable evidence;
- prevent accidental holdout fitting.

### Phase 7 — Robustness / Stability
Status: PLANNED

After a frozen candidate exists:
- parameter perturbation;
- time-window stability;
- market-regime slices;
- execution-semantic sensitivity;
- trade-order sensitivity where applicable;
- multiple-testing awareness;
- degradation analysis.

Optimization may discover candidates, but cannot declare canonical rules.

### Phase 8 — Untouched Validation
Status: PLANNED

Run the frozen candidate exactly once against the reserved validation dataset under its registered identity.

No:
- parameter fitting;
- geometry changes;
- threshold tuning;
- retrospective rule edits.

Failure returns the candidate to research.

### Phase 9 — Fresh Holdout
Status: PLANNED

Final unseen dataset with independent immutable identity.

The holdout exists to test whether the previously frozen candidate generalizes beyond development and validation evidence.

### Phase 10 — Forward Validation / MT5 Reconciliation
Status: EXISTING SEPARATE WORKSTREAM

Continue the live-demo forward test independently.

The Factory will later consume forward evidence through an explicit reconciliation boundary rather than modifying the runner.

Requirements:
- Python ↔ MT5 lifecycle parity;
- order/fill/SL/TP reconciliation;
- Telegram/event evidence where applicable;
- exact execution semantics;
- discrepancy classification;
- no silent correction of historical results.

### Phase 11 — Production Eligibility
Status: NOT ELIGIBLE

Production requires all required source, geometry, execution, statistical, validation, holdout, and forward gates to pass.

Production authorization must remain an explicit governance decision. The Factory must never autonomously turn a backtest result into a live BUY/SELL rule.

## Future deployment direction

The Factory is intentionally being built deployment-neutral.

Target topology:

Development PC
→ Git / artifacts / deterministic contracts
→ local or CI worker
→ VPS/cloud research workers
→ centralized evidence/artifact store
→ optional live research dashboard

The PC does not need to remain online for historical Factory research once a worker environment exists.

The MT5 forward-validation process is separate: it must remain continuously available somewhere (PC or VPS) while live forward testing is active.

## Future Live Factory UI — design only, not implementation

A later dashboard may present the Factory as a live research floor:
- worker/job states;
- queued/running/validating/completed jobs;
- real backend event stream;
- dataset and run identity;
- evidence status;
- validation gates;
- optional live XAUUSD/MT5 panel.

UI workers/animations must be driven by real backend events, not fake activity.

The live market panel must remain separate from research decision logic.

## Explicit non-goals for the current phase

Do not:
- invent unresolved SP2L geometry;
- build a production signal generator;
- connect the Factory to live order execution;
- optimize Strategy A before source resolution;
- use historical performance to decide source meaning;
- consume validation/holdout data for development;
- replace tick-feasible execution with M1-bar hindsight;
- add cloud infrastructure before the local deterministic pipeline is proven;
- modify the active forward runner merely to support Factory development.

## Immediate next milestone

Build Phase 1: Research Job Runner Contract.

Acceptance target:

ResearchJobSpec → validated dataset/test → ResearchRun → ExecutionAdapter → ExecutionReceipt → EvidenceBundle → acceptance gates

with deterministic behavior and a complete test suite, while leaving the live forward-test workstream untouched.
