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

### Historical Data Adapter / Dataset Ingestion

Added:
- src/strategy_factory/data.py
- tests/test_dataset_adapter.py

The adapter establishes the historical-data boundary without parsing or transforming market data.

Properties:
- raw bytes are the content identity;
- SHA-256 and byte-size are verified against the payload;
- concrete DatasetArtifact identity is registered through DatasetRegistry;
- registered dataset fingerprints can be re-verified deterministically;
- validation/holdout immutability and locking remain enforced by the registry;
- no resampling, timezone conversion, bar construction, or strategy interpretation occurs here.

This layer is an ingestion/identity boundary, not a market-data parser or execution engine.

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

### Synthetic End-to-End Execution

Added:
- src/strategy_factory/synthetic.py
- tests/test_synthetic_execution.py

The synthetic layer provides a controlled, deployment-neutral execution adapter for infrastructure validation only.

Properties:
- fixture-defined metrics and explicit execution semantics;
- deterministic execution IDs and input fingerprints derived from canonical inputs;
- separate BAR_CLOSE_RESEARCH and TICK_FEASIBLE fixtures;
- deliberate semantics mismatch rejection;
- no SP2L geometry, signal generation, optimization, or production logic.

The synthetic adapter is intentionally not a market simulator. It exists to prove the Factory orchestration and provenance contracts before real historical data or strategy execution are introduced.

### Research Job Runner

Added:
- src/strategy_factory/runner.py
- tests/test_research_job_runner.py

The runner provides the orchestration boundary:

ResearchJobSpec → validated test/dataset identity → ResearchRunIdentity → ExecutionAdapter → ExecutionReceipt → EvidenceBundle → acceptance gates

Properties:
- orchestration only;
- no SP2L geometry;
- no BUY/SELL generation;
- no optimization;
- preserves declared execution semantics;
- rejects adapter identity mismatches and incomplete execution;
- derives evidence metrics from the accepted receipt;
- prevents duplicate completion within one runner instance;
- produces reproducible run/evidence fingerprints for identical inputs.

## Current verification status

Phase 1 verification:
- ResearchJobRunner tests: 10 passed
- Full Factory contract suite: 99 passed

Phase 1 is frozen as verified.

Phase 2 implementation:
- Synthetic execution tests added.
- Local verification is pending.

## Roadmap — path forward

### Phase 1 — Complete the orchestration boundary
Status: VERIFIED — 99 TESTS PASS

Completed:
1. Research Job Runner contract.
2. Validate job against registered dataset/test identity.
3. Create or bind ResearchRunIdentity.
4. Delegate to ExecutionAdapter.
5. Produce ExecutionReceipt.
6. Produce EvidenceBundle only from the receipt.
7. Run execution and evidence-acceptance gates.
8. Return a deterministic run result.
9. Tests for successful, duplicate, identity-mismatch, dataset-mismatch, incomplete, reproducible, and semantics-preserving execution.

Next:
- pull the Factory branch;
- run runner tests;
- run the full Factory suite;
- freeze Phase 1 only after all tests pass.

### Phase 2 — Synthetic end-to-end execution
Status: VERIFIED — 110 TESTS PASS

Build a small deterministic synthetic execution adapter whose inputs and expected outputs are completely controlled by fixtures.

Implemented:
- controlled synthetic fixtures;
- deterministic execution IDs and input fingerprints;
- BAR_CLOSE_RESEARCH and TICK_FEASIBLE separation;
- semantics mismatch failure path;
- end-to-end runner coverage.

Purpose:
- prove Job → Run → Adapter → Receipt → Evidence end-to-end;
- prove deterministic fingerprints;
- prove repeatability across processes/environments;
- exercise BAR_CLOSE_RESEARCH and TICK_FEASIBLE as separate declared semantics;
- verify failure isolation.

This phase is infrastructure validation, not Strategy A validation.

### Phase 3 — Historical data adapter / dataset ingestion
Status: VERIFIED — 120 TESTS PASS

Create a deployment-neutral historical-data boundary.

Implemented:
- deterministic raw-byte ingestion;
- SHA-256 and byte-size identity;
- DatasetArtifact registration;
- exact registered-identity verification;
- validation/holdout lock enforcement through DatasetRegistry;
- no parsing, resampling, timezone conversion, or strategy interpretation.

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
Status: VERIFIED — 130 TESTS PASS

Added:
- src/strategy_factory/execution_kernel.py
- tests/test_execution_kernel.py

The kernel is strategy-agnostic and defines only generic execution mechanics:
- strictly chronological market-event processing;
- explicit BUY/SELL entry instructions;
- deterministic SL/TP lifecycle;
- explicit BAR_CLOSE_RESEARCH vs TICK_FEASIBLE semantics;
- explicit same-event ambiguity policy;
- blocked ambiguity as a first-class outcome;
- deterministic R accounting, gross profit/loss, PF, and drawdown metrics.

Critical boundary:
- TICK_FEASIBLE requires ordered observations; an OHLC bar is never treated as an ordered tick stream.
- BAR_CLOSE_RESEARCH may expose same-event SL/TP ambiguity, but the chosen resolution policy must be explicit.
- No SP2L geometry, trailing rule, P-Gap logic, fill semantics, or production order logic is implemented here.


Build the execution kernel independently from SP2L-specific signal geometry.

Verification completed 2026-10-06:
- execution-kernel suite: 10 passed;
- full Factory suite including the kernel: 130 passed;
- TICK_FEASIBLE now requires explicit bid/ask observations;
- OHLC-only observations are rejected under TICK_FEASIBLE;
- same-bar ambiguity remains explicit under BAR_CLOSE_RESEARCH;
- entry/exit sequence provenance is deterministic;
- no SP2L geometry or production execution logic was introduced.

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

### Phase 5 — SP2L Strategy Engine / Source Resolution
Status: SOURCE RESOLUTION ACTIVE — FROZEN GEOMETRY BLOCKED

Source-resolution ledger expanded from 6 to 18 explicit blocking questions.

Confirmed source meaning remains limited to what the evidence supports:
- P.GAP is distinct from Common GAP; valid BO is P-Gap.
- F12 describes BUY retrace to previous-candle Low and SELL retrace to previous-candle High, but executable interaction/fill semantics remain unresolved.
- F13 confirms the 2X secondary-entry 50% relation; complete execution/management semantics remain unresolved.
- F10 places the stop behind the candle where the Spike started, but the exact anchor remains unresolved.
- C04 confirms the trade-template concepts SL / Entry / TP1 / TP2 / 2X, without freezing unsupported formulas.
- C05 references the 15-minute MA50, while exact timeframe/MA semantics remain unresolved.
- C06 references deletion of an unfilled Buy Limit within 1–2 candidate candles; exact deterministic lifecycle semantics remain unresolved.

Additional source-gated questions now explicitly tracked:
- P-Gap OHLC construction, referenced candles, equality boundaries, and relevant High/Low selection.
- Entry and Leg-2-origin anchors.
- AB=CD A/B/C/D anchors and tolerance.
- TP1 and TP2 formulas.
- Full 2X execution/sizing/target/reward-management semantics.
- Bearish symmetry.
- Exact timeframe/MA semantics.

Primary source archive status independently remains: G4 exact OHLC endpoints UNRESOLVED, F10 stop geometry UNRESOLVED, F14 AB=CD anchors/tolerance PARTIAL/UNRESOLVED, F15 bearish mirror source-consistent but not independently frozen, Frozen Geometry BLOCKED.

No canonical Strategy Engine implementation is permitted while any blocking question remains OPEN.

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

Verify Phase 4 locally with the execution-kernel suite and the full Factory suite.

After Phase 4 is green, freeze the generic execution mechanics and proceed to Phase 5 only after source resolution/frozen geometry permits a Strategy Engine.

The active forward-test workstream remains untouched.
