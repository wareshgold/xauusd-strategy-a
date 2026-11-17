# SP2L Factory Runner–Orchestrator–Worker–Evidence Boundary Audit
Date: 2026-11-17
Branch: research/architecture-consolidation-plan-20261117
Scope: static GitHub source and test inspection only
Status: Phase 0 audit finding; no implementation authorized

## Executive conclusion
Keep ResearchJobRunner, FactoryOrchestrator, FactoryWorker/Fleet, FactoryJobEventLedger, ResearchRecordLedger, and the statistical/stability evidence acceptance chain as distinct responsibilities. The current separation is conceptually sound. Do not merge them into one Factory service or treat operational telemetry as research evidence.

The principal gap is not class duplication. It is the absence of a single durable, recoverable transaction boundary spanning job dispatch, adapter execution, run/evidence registration, research-record creation, and lifecycle event persistence. A second gap is that the later statistical/stability ResearchAcceptance chain is separate from the Runner's initial receipt-level evidence acceptance; the two acceptance meanings must remain explicitly named and must not be conflated.

## Inspected sources
- src/strategy_factory/runner.py
- src/strategy_factory/orchestrator.py
- src/strategy_factory/worker.py
- src/strategy_factory/job_events.py
- src/strategy_factory/telemetry.py
- src/strategy_factory/jobs.py
- src/strategy_factory/research_record.py
- src/strategy_factory/handoff.py
- src/strategy_factory/research_evidence_bundle.py
- src/strategy_factory/research_evidence_ledger.py
- src/strategy_factory/research_acceptance.py
- tests/test_research_job_runner.py
- tests/test_factory_job_events.py
- tests/test_factory_handoff.py
- tests/test_factory_e2e_smoke.py

Tests were read as source only; they were not executed.

## Confirmed responsibility boundaries
1. ResearchJobSpec is a deterministic, deployment-neutral declaration of job identity and inputs. It is not an execution plan or strategy-rule authority.
2. ResearchJobRunner validates the job against HistoricalTestSpec, readiness snapshot, dataset provenance, creates a run, calls the injected adapter, validates the receipt, records receipt-derived EvidenceBundle, evaluates execution/acceptance/provenance gates, and creates a ResearchRecord.
3. FactoryOrchestrator owns FIFO queueing, dispatch, worker lifecycle calls, operational events, and explicit station handoff. It delegates actual research execution through an injected callable.
4. FactoryWorker/Fleet represent operational worker state and publish status telemetry. They do not establish research validity.
5. FactoryJobEventLedger is an operational lifecycle journal. Its own module documentation explicitly distinguishes it from strategy evidence.
6. ResearchRecord is a fingerprinted immutable binding of run, evidence, readiness snapshot, audit and provenance.
7. ResearchEvidenceBundle / ResearchEvidenceLedger / ResearchAcceptance form a separate higher-level chain binding a ResearchRecord to statistical and stability evidence. This is not the same contract as Runner.evidence_acceptance_gate.

## Findings and risks

### F1 — Runner side effects are not one atomic transaction
ResearchJobRunner creates/registers a run before calling the adapter. It registers Evidence, then audit/provenance, then ResearchRecord. If a later stage fails, earlier in-memory registrations may remain. The runner's _completed_jobs guard is process-instance memory only; it does not provide durable idempotency across restart or separate runner instances.

Impact: a retry after partial failure may encounter an already-created run or evidence without a complete ResearchRecord. Recovery behavior depends on lower-level ledger idempotency and caller behavior; no cross-ledger transaction or recovery journal is visible in the inspected runner.

Disposition: HIGH-PRIORITY CONTRACT GAP. Do not solve by merging ledgers. Define explicit job execution states and recovery/idempotency semantics before implementation.

### F2 — Orchestrator removes a job from the queue before execution
run_next pops the queued item before worker dispatch and adapter execution. On executor failure it records FAILED and re-raises, but the job is no longer pending in the in-memory queue. No retry queue, dead-letter state, or durable requeue contract is visible in this method.

Impact: process failure or executor error can leave a job failed with no deterministic retry path. The lifecycle journal may describe the failure, but it does not itself restore the queue.

Disposition: define retry policy and terminal/nonterminal failure states before changing queue mechanics. Do not silently auto-retry potentially non-idempotent research adapters.

### F3 — Event ledger persistence is append-oriented but not transactionally durable
FactoryJobEventLedger validates fingerprints and contiguous sequence when loading. append constructs and appends to the in-memory list before writing JSONL. The file append has no visible inter-process lock, fsync, atomic segment/commit protocol, or rollback if the write fails. Sequence allocation is local to one ledger instance.

Impact: concurrent writers or a process interruption can produce duplicate sequence values, partial final lines, or memory/disk divergence. Fingerprints detect altered event payloads but do not alone guarantee durable ordering or exactly-once append.

Disposition: preserve this as an operational event ledger, but specify single-writer ownership, crash recovery, corruption handling, and durability level. Do not present current JSONL as a complete transactional audit store.

### F4 — Event schema validates identity/fingerprint, not lifecycle transition legality
FactoryJobEvent.validate checks basic identity and payload fingerprint. It does not enforce a state machine such as QUEUED → DISPATCHED → COMPLETED/FAILED, worker ownership, or prohibition of duplicate terminal events. Orchestrator emits expected sequences in its normal path, but the ledger itself accepts arbitrary event_type strings and event order.

Impact: imported/replayed/corrupt event streams can be internally fingerprint-valid while semantically impossible.

Disposition: add a separately versioned lifecycle-stream validator/reducer contract; do not overload the event dataclass with strategy acceptance.

### F5 — Worker status is a replaceable projection, not history
telemetry.publish_workers writes a normalized worker roster to a temporary file and replaces the status file. This is appropriate for a latest-state dashboard projection. It is not an append-only event history. Worker heartbeat changes state to HEARTBEAT, while completion/failure updates later state.

Impact: dashboard status can be stale or lost independently of the event journal; it cannot serve as proof that every transition occurred.

Disposition: keep telemetry as a disposable read-only projection and rebuild it from authoritative lifecycle state where feasible. Clearly label freshness and source.

### F6 — Handoff is evidence-bound but event selection/uniqueness need stronger contracts
build_research_handoff selects the last matching COMPLETED event with an output artifact for the job and source station. validate_evidence_bound_handoff binds job/run fingerprint, record evidence ID, source event fingerprint, station and optional dataset identity. The handoff itself is fingerprinted and route-checked.

Gaps: selection is based on list order and matching fields; no explicit unique source-completion invariant is visible. Repeated calls can construct the same default handoff identity, while the event journal can contain multiple HANDOFF_ACCEPTED entries. The dataset SHA/artifact ID are caller-supplied values; this contract does not independently verify the artifact bytes.

Impact: ambiguous completion selection or duplicate handoff records can make station progression hard to reconstruct. Handoff binding is not dataset artifact verification.

Disposition: preserve Handoff as its own transition contract. Define one source completion per run/station, idempotency key, duplicate policy, and relationship to independently verified dataset artifacts.

### F7 — Two acceptance layers have different meanings
Runner calls evidence_acceptance_gate on the adapter receipt and EvidenceBundle, then evaluates provenance and creates ResearchRecord. Separately, evaluate_research_acceptance validates StatisticalEvidence and StabilityEvidence bound to that ResearchRecord, a combined ResearchEvidenceBundle, and ledger registration.

Impact: the word “accepted” can be misread as statistical/stability acceptance or production readiness when Runner.accepted only means all gates returned by that Runner invocation passed. The later ResearchAcceptance is also not production authorization.

Disposition: retain both layers but use explicit names in UI/docs, e.g. execution/evidence-registration acceptance versus statistical-and-stability research acceptance. Neither may imply canonical strategy authority, fresh holdout passage, or production authorization.

### F8 — Evidence and event journals are separate stores with no atomic cross-link
The completed operational event may include run fingerprint and evidence ID as output_artifact. ResearchRecord separately binds run, evidence, snapshot, audit and provenance. This is a useful cross-reference, but no atomic commit spans the event journal and research ledgers.

Impact: a crash can leave a COMPLETED event without a fully persisted record, or a record without a corresponding COMPLETED event, depending on failure timing and caller orchestration.

Disposition: define reconciliation states (event-only, record-only, both-consistent, conflict) and a read-only repair/reconciliation report before any automatic repair.

## Test coverage observed (not executed)
- Runner tests cover job/spec mismatch, dataset fingerprint mismatch, adapter identity/semantics and incomplete execution rejection, receipt-derived evidence, reproducible run identity, and no geometry dependency.
- Event tests cover fingerprint/filtering, normal queue lifecycle and executor failure.
- Handoff tests cover missing completed artifact, declared route, evidence-bound handoff, and route rejection.
- E2E synthetic smoke test covers adapter → evidence → record → handoff → StarNet projection and asserts production_locked=True and buy_sell_generation=0.
- The inspected tests do not establish process-crash recovery, concurrent writers, durable retry/idempotency across restarts, partial JSONL writes, cross-ledger reconciliation, or duplicate handoff behavior.

## Recommended architecture disposition
KEEP SEPARATE:
- ResearchJobRunner: research execution and evidence/provenance orchestration.
- FactoryOrchestrator: queue and station lifecycle coordination.
- FactoryWorker/Fleet: worker state and heartbeat.
- FactoryJobEventLedger: operational event journal.
- telemetry: latest-state dashboard projection.
- ResearchRecordLedger: immutable accepted-run record registry.
- Statistical/stability evidence bundle, ledger and ResearchAcceptance: higher-level research validation chain.
- Handoff: explicit stage transition binding.

DO NOT:
- merge the Runner and Orchestrator;
- treat worker telemetry or job events as statistical evidence;
- treat Runner.accepted as production eligibility;
- infer canonical SP2L geometry or execution semantics from Factory acceptance;
- auto-retry adapters before idempotency/recovery semantics are specified;
- make live runner/MT5 changes as part of this architecture audit.

## Next Phase 0 work
1. Inspect lower-level run/evidence/audit ledgers and their idempotency/error behavior.
2. Trace all call sites of build_runner_executor, ResearchJobRunner.run, FactoryOrchestrator.run_next, handoff, and ResearchAcceptance to establish the actual end-to-end caller contract.
3. Inspect persistence configuration and process ownership for the event journal and worker telemetry.
4. Write synthetic failure fixtures for interruption points only after the intended recovery semantics are source-resolved and explicitly approved.
5. Keep Phase 0 OPEN until these contracts and all relevant consumers are inventoried.

## Safety and scope
Static source inspection only. No code execution, tests, MT5 initialization, broker access, live runner access, configuration changes, artifact mutation, or canonical strategy decisions were performed. This report is an audit finding, not implementation approval.
