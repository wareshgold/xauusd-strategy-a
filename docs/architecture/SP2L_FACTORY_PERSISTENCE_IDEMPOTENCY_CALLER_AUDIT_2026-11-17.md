# SP2L Factory Persistence, Idempotency and Caller-Contract Audit
Date: 2026-11-17
Branch: research/architecture-consolidation-plan-20261117
Scope: static GitHub tree/source/test inspection only
Status: Phase 0 OPEN; no implementation authorized

## Executive conclusion
The lower-level audit confirms that the main Run, Evidence and ResearchRecord registries are in-memory only. The job event journal is optionally JSONL-persisted, but its current append/load behavior does not establish crash-safe, multi-process transactional durability. The statistical/stability evidence ledger is also in-memory only.

Consequently, the current Factory can demonstrate deterministic synthetic wiring in one process, but the inspected contracts do not yet establish durable restart recovery, exactly-once execution, or automatic reconciliation after a partial failure. Do not add automatic retries or merge ledgers before these semantics are explicitly specified.

## Sources inspected
- src/strategy_factory/runs.py
- src/strategy_factory/usage.py
- src/strategy_factory/evidence.py
- src/strategy_factory/research_record.py
- src/strategy_factory/runner.py
- src/strategy_factory/orchestrator.py
- src/strategy_factory/job_events.py
- src/strategy_factory/telemetry.py
- src/strategy_factory/handoff.py
- src/strategy_factory/research_evidence_bundle.py
- src/strategy_factory/research_evidence_ledger.py
- src/strategy_factory/research_acceptance.py
- src/strategy_factory/acceptance.py
- src/strategy_factory/research_provenance.py
- tests/test_research_job_runner.py
- tests/test_research_evidence_ledger.py
- tests/test_factory_job_events.py
- tests/test_factory_handoff.py
- tests/test_factory_e2e_smoke.py

The recursive Git tree was retrieved without truncation (446 Python/TypeScript/JavaScript source/test candidates). GitHub code search returned no matches for the call-site queries on the connected search index, so this report does not claim a complete repository-wide call-site graph. Tests were read as source only and were not executed.

## Confirmed persistence model

### In-memory registries
- ResearchRunLedger stores run identities in a process-local dict.
- EvidenceLedger stores evidence bundles in a process-local dict.
- ResearchRecordLedger stores records in a process-local dict.
- ResearchEvidenceLedger stores entries in a process-local list.
- DatasetUsageLedger is used by ResearchRunLedger; the inspected Run/Evidence/Record chain does not expose a durable backing store.
- The objects enforce immutable identity/conflict checks within their current instance, but a new process starts with empty registries unless an external caller reconstructs them. No such durable reconstruction protocol was found in the inspected modules.

### Job event journal
FactoryJobEventLedger defaults to runtime/factory_job_events.jsonl and reloads all lines at construction, validating each fingerprint and contiguous sequence. append allocates sequence from the instance-local list, appends to memory, then appends one JSONL line to disk. No inter-process lock, fsync, atomic append transaction, or explicit partial-final-line recovery is visible. A malformed/truncated line can cause construction to fail during JSON parsing. Multiple ledger instances can allocate the same next sequence.

### Worker telemetry
publish_workers writes a latest-state snapshot using a temporary file, flush/fsync and os.replace. This is a useful atomic projection, but it is not a history or a durable queue. It cannot independently prove all job transitions.

## Failure and replay analysis

### F1 — Run creation precedes adapter execution
ResearchJobRunner.run registers dataset usage and creates the run before invoking adapter.execute. If the adapter fails, the run remains registered in the current in-memory registries. The orchestrator records FAILED, but no compensating transaction removes or marks the Run as incomplete.

### F2 — Evidence can exist without a completed ResearchRecord
After adapter success, Runner registers Evidence before acceptance/audit/provenance and ResearchRecord creation. A failure in a later stage can leave Run and Evidence present but no ResearchRecord. There is no explicit durable RUN_STARTED / EVIDENCE_REGISTERED / RECORD_COMMITTED recovery state machine in the inspected runner.

### F3 — Fresh Runner replay re-executes the adapter
The completed-job guard is process-local. A new ResearchJobRunner can replay the same immutable job. Run and Evidence ledgers can return an identical existing object for matching IDs, but the adapter is called again. This is deterministic replay only if adapter behavior and external side effects are themselves replay-safe. No durable execution claim/lease or idempotency token is passed to the adapter contract here.

### F4 — Orchestrator queue is not durable
The queue is a process-local list. run_next removes the job before dispatch. On exception, it writes FAILED and re-raises; there is no durable queue restore/retry/dead-letter contract in the inspected orchestrator. Restart loses queued-but-not-dispatched jobs unless another layer reconstructs them.

### F5 — Event ledger crash/concurrency limitations
Fingerprinting detects payload alteration, and load checks contiguous sequence. It does not provide writer serialization, crash-safe append, exactly-once append, or semantic state-machine validation. Because memory is updated before disk append, an I/O failure can also leave the current instance's memory ahead of disk.

### F6 — Handoff object itself is not durably registered
build_research_handoff returns a fingerprinted ResearchHandoff. FactoryOrchestrator.handoff appends a HANDOFF_ACCEPTED event, but the event stores the evidence ID and destination metadata, not the handoff fingerprint or full handoff payload. No persistent handoff registry was found in the inspected path. A later reader cannot reconstruct/verify the exact handoff object from the event alone.

### F7 — Handoff source completion selection can be ambiguous
build_research_handoff selects the last matching COMPLETED event for a job and source station. It does not require exactly one qualifying completion or reject multiple qualifying completions. Duplicate handoff attempts can append multiple HANDOFF_ACCEPTED events; there is no explicit unique idempotency key or duplicate policy.

### F8 — Job purpose is not bound into ResearchJobSpec
ResearchJobSpec fingerprints strategy/test/dataset/parameters/objective/execution semantics. Runner accepts a separate purpose argument, and the run identity includes purpose. Since purpose is not a ResearchJobSpec field, the same job fingerprint can be invoked with a different purpose by the caller. The inspected provenance comparison does not compare run.purpose to a job-declared purpose.

Impact: job identity does not fully declare all inputs that influence the resulting ResearchRunIdentity.

Disposition: resolve whether purpose is a job input, a stage policy, or caller context, then bind and validate it explicitly. Do not silently infer it.

## Acceptance layers
1. Runner evidence_acceptance_gate verifies receipt/run/evidence identity and descriptive metric consistency. Runner then evaluates provenance and creates a ResearchRecord. This is execution/evidence-registration acceptance.
2. ResearchEvidenceBundle binds StatisticalEvidence and StabilityEvidence to a ResearchRecord.
3. ResearchEvidenceLedger registers the bundle in memory and prevents conflicting entries for one run in that ledger instance.
4. evaluate_research_acceptance requires exact record/statistical/stability/bundle binding and ledger registration.

These are distinct assurance layers. Neither acceptance layer authorizes production, establishes canonical Strategy A geometry, or replaces untouched validation, robustness/stability review, or fresh holdout. The statistical/stability ledger's in-memory nature means its registration is not restart-durable in the inspected implementation.

## Caller graph coverage and limits
- The direct orchestration path is confirmed in source: FactoryOrchestrator.run_next invokes the injected executor; build_runner_executor calls ResearchJobRunner.run; the E2E synthetic test wires Runner → Evidence → ResearchRecord → Handoff → StarNet projection.
- The synthetic E2E test asserts production_locked=True and buy_sell_generation=0.
- scripts/run_sp2l_factory_discovery_mt5.py and DiscoveryFactory were previously identified as an MT5-backed discovery entry path; they remain blocked from execution.
- GitHub code search returned no results for build_runner_executor, ResearchJobRunner(, FactoryOrchestrator( and evaluate_research_acceptance( in its available index. This is not evidence that no call sites exist. Full branch-wide call-site enumeration remains open and requires a branch-aware source scan.
- No runtime, workflow, local PC, or external consumer behavior was inferred beyond the inspected sources.

## Required contracts before implementation
1. Durable job identity: bind every execution-affecting input, including purpose/stage policy, to a versioned job contract.
2. Execution idempotency: define a stable execution key, adapter side-effect rules, and behavior after timeout/unknown completion. Do not assume a retry is safe.
3. Run/evidence/record commit model: define explicit states and a recovery/reconciliation report for run-only, run+evidence, record-only, event-only, and consistent cases.
4. Queue durability: define persisted submission, claim/lease, dispatch, terminal state, retry policy and dead-letter semantics.
5. Event journal: define single-writer or locking model, append durability, schema versioning, partial-line recovery policy, sequence allocation, and lifecycle transition validation.
6. Handoff durability: persist the complete handoff identity/fingerprint or make the event sufficient to reconstruct it; define uniqueness and duplicate behavior.
7. Acceptance naming: distinguish execution/evidence registration from statistical/stability research acceptance in APIs, telemetry and dashboard labels.
8. Persistence implementation choice: select and document a durable store only after requirements and failure fixtures are approved. This report does not prescribe a database or schema.

## Recommended disposition
KEEP distinct: Runner, Run/Evidence/Record registries, Orchestrator, Worker/Fleet, Event Ledger, telemetry projection, Handoff, and Statistical/Stability Evidence acceptance.

DO NOT:
- add automatic retries;
- infer exactly-once behavior from fingerprints;
- treat in-memory ledgers as restart-persistent;
- treat a COMPLETED event as proof that ResearchRecord is durably committed;
- treat HANDOFF_ACCEPTED as a complete handoff record;
- equate Runner acceptance with statistical/stability acceptance or production readiness;
- execute MT5-backed discovery or forward operations during this audit.

## Next Phase 0 actions
1. Complete branch-aware caller enumeration for all 446 source/test candidates, with special attention to scripts, workflows, dashboard launchers and external entrypoints.
2. Map every persistent runtime path and process owner, including whether more than one process can write the event journal.
3. Agree on the desired crash/retry/reconciliation semantics before writing synthetic failure fixtures.
4. Keep Phase 0 OPEN. No code refactor, file moves, deletes, merges, MT5 access, runner changes or canonical strategy decisions are authorized by this audit.
