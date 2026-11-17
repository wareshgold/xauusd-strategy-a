# SP2L Architecture Consolidation Plan — 2026-11-17

## Status

- Classification: research-only architecture plan
- Status: PROPOSED — NOT APPROVED FOR IMPLEMENTATION
- Canonical Strategy A rules changed: NO
- Trading/execution behavior changed: NO
- MT5 or broker accessed: NO
- Files or evidence deleted: NO
- Branch: `research/architecture-consolidation-plan-20261117`
- Base branch: `research/sp2l-starnet-engine-integration-20261007`
- Base commit: `befec09c752e8d7ba9d10ff75d4e39ad5351c853`

This document is a consolidation plan, not a refactor. Classifications are provisional until dependency, runtime-entrypoint, test, artifact, and ownership audits are complete. No module is authorized for deletion by this document.

## 1. Objectives and non-negotiable constraints

The objective is to reduce architectural duplication and make the research-to-validation path understandable without discarding evidence, changing Strategy A semantics, or disturbing the active forward runner.

The following rules remain binding:

1. Source meaning outranks backtest performance.
2. Only source-confirmed rules may become canonical. Unresolved geometry remains unresolved.
3. Do not invent a P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.
4. Preserve the workflow: SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.
5. AI may assist research, engineering, validation, documentation, and analytics; it may not autonomously define canonical rules or generate production BUY/SELL decisions.
6. Research, backtest, dashboard, and evidence tooling must not initialize or connect to MT5 unless a separately approved operational task explicitly requires it.
7. The active V3.1 forward runner is outside the scope of this consolidation. No import rewiring, configuration edits, process restart, or execution change is permitted.
8. Evidence, raw exports, manifests, hashes, fixtures, and historical audit reports are immutable inputs. Reorganization must preserve byte identity or record a separately verified copy with provenance.
9. No branch deletion, history rewrite, bulk file deletion, or broad merge is part of this plan.

## 2. Repository baseline and confidence

This plan was prepared from GitHub source/tree inspection on 2026-11-17. The primary inspected architecture branch is:

- `research/sp2l-starnet-engine-integration-20261007`
- HEAD: `befec09c752e8d7ba9d10ff75d4e39ad5351c853`

The user's local worktree was separately reported on branch `research/sp2l-starnet-engine-integration-20261007`, HEAD `befec09c`, with 135 status entries. That local worktree is dirty. It must not be pulled, checked out, reset, cleaned, or used as a refactor workspace until its changes have been safely inventoried and preserved.

The following additional branch exists and contains later multi-account/recovery/evidence-contract work:

- `research/multi-account-foundation-rfc-20261116`

The two branches have diverged substantially. A direct merge is explicitly NOT recommended. The earlier comparison reported 533 commits unique to the StarNet integration side and 187 unique to the multi-account side; this is a branch-history observation, not a measure of code overlap or merge difficulty. A later compare against `main` also showed the StarNet integration branch is substantially divergent from main. Therefore, the base branch chosen for this planning document is a working reference only, not a declaration that it is the permanent production/main branch.

Inspection is not yet exhaustive. In particular, full dependency graphs, all script entrypoints, all CI workflows, all artifact references, runtime imports, and the complete multi-account branch diff still require a structured inventory. Counts from an earlier top-level listing are approximate and must not be used as acceptance criteria.

## 3. Target architecture

The target is a small number of explicit layers with one owner for each responsibility.

### A. Research Core

Owns source interpretation records, frozen geometry contracts, synthetic fixtures, deterministic strategy evaluation, and reproducible backtest inputs/outputs.

It must not depend on MT5 terminal APIs, Telegram, dashboards, or account credentials.

### B. Evidence and Data Layer

Owns immutable data intake, manifests, provenance, exact-byte verification, observation records, artifact linkage, and evidence completeness/recovery contracts.

It must distinguish:
- raw provider/API observations;
- exported artifacts;
- normalized records;
- derived analytics;
- manifest declarations;
- verification results.

An artifact hash proves byte identity only. It does not by itself prove source provenance, query scope, API completeness, or that an artifact belongs to a particular observation.

### C. Validation Factory

Owns deterministic job orchestration and gated stages:
- source/geometry readiness;
- fixture execution;
- development checks;
- untouched validation;
- robustness/stability;
- fresh holdout.

The Factory may schedule and report jobs. It may not promote unresolved rules or turn statistical results into canonical strategy semantics.

### D. Forward Operations Boundary

Owns operational MT5 adapters, account isolation, order/deal/position lifecycle, recovery, broker constraints, and forward telemetry.

This boundary is separate from Research Core and is not a general-purpose dependency for backtests. Operational actions require explicit authorization and independent safety checks.

### E. Presentation

Owns dashboard and StarNet rendering of already-produced telemetry. Presentation must be read-only with respect to research jobs, account state, and trading execution. Demo telemetry must remain unmistakably separate from actual telemetry.

## 4. Module disposition register

The labels below are initial recommendations, not completed dependency findings.

| Area / current location | Proposed disposition | Rationale and required proof |
|---|---|---|
| `src/domain/strategy-a/` | KEEP; audit boundaries | Preserve the TypeScript strategy-domain model as research/domain code. Verify it does not silently encode unresolved geometry as canonical. Do not merge it into Python until semantic parity and ownership are demonstrated. |
| `src/backtest/` | KEEP; MERGE duplicate orchestration only if proven | Keep deterministic backtest contracts and adapters. Identify whether engine, adapter, replay, and data loading responsibilities are duplicated by Python research scripts. No result parity assumption without fixtures. |
| `src/strategy_factory/` | KEEP; CONSOLIDATE internal orchestration | Retain one Factory domain and one public orchestration entrypoint. Review `factory.py`, `runner.py`, `orchestrator.py`, `worker.py`, job/event/state modules, gates, and StarNet adapter. Merge only overlapping responsibilities; do not collapse distinct lifecycle roles. |
| `src/strategy_factory/gates.py` and `models.py` | KEEP; reconcile gate vocabulary | Gate stages and status models should map to the mandated workflow. Current older stage labels (Strategy Lab/Engine/Test Factory/Forward Validation) need an explicit crosswalk, not silent renaming. |
| `src/strategy_factory/starnet_adapter.py` | KEEP; isolate under presentation adapter | Renderer-neutral adapter should consume normalized telemetry only. Keep strategy decisions and job execution out of it. |
| `scripts/factory_dashboard.py`, `scripts/factory_starnet_world.py` | MERGE entrypoint surface; KEEP separate renderers | Aim for one documented dashboard launch command and one telemetry contract. Preserve alternate renderers where they provide distinct presentation. |
| `scripts/factory_demo.py` | KEEP as isolated demo utility | It writes demo telemetry and must never write into live telemetry paths or invoke strategy/MT5 execution. |
| `scripts/` research/backtest/replay/forensic scripts | RELOCATE by responsibility after inventory | Group into acquisition, replay/backtest, analysis, evidence, validation, and operations namespaces. Keep historical one-off scripts in a clearly marked archive only after dependencies and reproducibility are checked. |
| `scripts/run_sp2l_*forward*` and live gateways | BLOCKED from refactor | Operationally sensitive. No import, configuration, account, terminal, process, or behavior changes under this plan. |
| `scripts/mt5_history_reconciliation.py` and other MT5-initializing tools | BLOCKED from execution; source audit only | These tools may initialize a live terminal. Inspect source statically; do not run as part of offline tests. Separate live acquisition from offline reconciliation. |
| `tests/` | KEEP; reorganize by contract | Tests are executable specifications. Preserve all tests and fixture bytes. Move only with imports updated and full test parity demonstrated. |
| `docs/research/` | KEEP; INDEX and ARCHIVE | Research documents are evidence/history. Add an index and status taxonomy; do not bulk-delete or rewrite historical conclusions. |
| `artifacts/`, `data/`, manifests, CSV/JSON/JSONL | KEEP immutable; classify | Separate source/raw, derived, report, and runtime output. Never delete based only on age, filename, size, or duplicate-looking content. Verify hash and references before any move. |
| `vendor/starnet-engine` / bootstrap | KEEP optional integration; review license and pin | StarNet is a renderer/integration dependency, not the Factory domain or source of strategy semantics. Pin exact upstream commit and keep it optional for headless tests. |
| Multi-account / recovery / history evidence modules from `research/multi-account-foundation-rfc-20261116` | BLOCKED pending selective integration audit | Preserve branch as source of work. Do not merge branch wholesale. Map each contract, test, and dependency to the target Forward Operations/Evidence boundary, then port in small reviewable units. |
| Legacy or duplicate branches | BLOCKED pending branch/evidence archive audit | No branch deletion until unique commits, tags, artifacts, and source-resolution decisions are preserved and an explicit retention decision is recorded. |

## 5. Factory consolidation rules

The Factory should expose one documented command/API for submitting and observing research jobs. Internally, responsibilities remain separate:

- **Factory service:** validates job requests and stage eligibility.
- **Orchestrator:** schedules jobs and coordinates workers.
- **Worker:** executes one bounded job and emits lifecycle events.
- **Journal/event store:** records append-only job events and handoffs.
- **Gate evaluator:** evaluates explicit evidence predicates.
- **Telemetry projection:** produces a stable read model for dashboard clients.
- **Renderer adapter:** maps read-model data to StarNet or another renderer.

Do not merge these merely to reduce file count. Consolidation is justified only when two modules have the same owner, lifecycle, invariants, and test contract. A single module must not both execute jobs and render UI or make strategy promotion decisions.

Factory job outputs must be immutable/versioned artifacts. Handoffs must reference a completed output artifact and an auditable event sequence. A dashboard view is never authoritative evidence of a job passing.

## 6. Multi-account integration boundary

Multi-account work is not part of the Research Core. Its intended location is Forward Operations, with a strict account-scoped boundary.

Before porting anything from the multi-account branch, produce a mapping for:
- account identity and isolation;
- terminal/session ownership;
- read-only history acquisition;
- order/deal/position linkage;
- history completeness and stability;
- recovery eligibility and fail-closed behavior;
- evidence manifest and artifact binding;
- account-specific notification routing;
- operational permission gates.

No account credentials, terminal connections, MT5 initialization, broker calls, or live runner changes are permitted during the integration audit.

### Explicit unresolved blocker: history capture producer and artifact binding

The source audit recorded in `docs/research/SP2L_ARTIFACT_TO_OBSERVATION_BINDING_SOURCE_RESOLUTION_2026-11-16.md` concluded `BINDING_CONTRACT_UNRESOLVED` and `CAPTURE_PRODUCER_NOT_FOUND_IN_INSPECTED_SOURCES`.

Do not invent:
- artifact-to-observation cardinality;
- ORDERS versus DEALS artifact role semantics;
- API invocation identifiers or query scope binding;
- serialization field/order/type/null/timestamp rules;
- payload fingerprint algorithms;
- empty/error/partial/interrupted capture semantics.

The next valid action is to locate and inspect the actual capture producer or authoritative specification. If none exists, obtain an explicit user decision before defining the contract.

## 7. Script and documentation taxonomy

Proposed future organization (logical grouping first; physical moves only after dependency audit):

```text
scripts/
  acquisition/       # explicit data acquisition; operational access gated
  backtest/          # deterministic historical replay
  research/          # hypothesis and exploratory analysis
  validation/        # fixtures, stability, robustness, holdout
  evidence/          # manifests, verification, offline reconciliation
  operations/        # MT5/forward entrypoints; isolated and guarded
  factory/           # Factory service/dashboard entrypoints
  archive/           # retained historical one-off tools, not on default path

docs/
  architecture/      # current system boundaries and decisions
  operations/        # guarded runbooks and operational contracts
  research/
    index.md         # current index by topic/status
    archive/         # historical snapshots and superseded checkpoints
```

This is a target taxonomy, not an instruction to move files now. Preserve import paths and command compatibility until a migration plan and tests exist.

## 8. Deprecation policy

A module may be marked DEPRECATE only when all of the following are true:

1. No production/forward entrypoint imports or invokes it.
2. No tests, CI workflow, scheduled task, runbook, or user workflow depends on it.
3. Its unique evidence, behavior, and decisions are preserved elsewhere with exact references and hashes where applicable.
4. A replacement exists and has equivalent or intentionally changed behavior documented.
5. A deprecation window and rollback path are documented.
6. The user explicitly approves removal.

Until then, use `DEPRECATE-CANDIDATE` or `BLOCKED`, not deletion.

## 9. Implementation sequence and gates

### Phase 0 — Freeze and inventory
- Confirm target base branch with user.
- Preserve dirty local worktree; do not pull into it.
- Export branch/commit inventory and branch archive map.
- Build a path inventory with file type, owner, import references, entrypoint references, test references, CI references, and artifact references.
- Identify operationally sensitive modules without executing them.

Exit: inventory is complete enough that every proposed move/merge has known references and an owner.

### Phase 1 — Architecture contracts
- Publish one architecture map and module ownership table.
- Define Research Core ↔ Evidence ↔ Factory ↔ Forward Operations ↔ Presentation interfaces.
- Record unresolved interface questions as blockers.
- Align Factory gate vocabulary with the mandated research workflow.

Exit: contracts reviewed; no strategy geometry or execution semantics invented.

### Phase 2 — Factory internal consolidation
- Select one public Factory entrypoint.
- Consolidate duplicate orchestration paths only where invariants and tests match.
- Keep worker lifecycle, journal, gate evaluation, telemetry projection, and renderer adapter distinct.
- Add/retain headless tests proving no MT5 import/initialization in Factory core.

Exit: existing Factory tests pass; old entrypoints either remain compatible or have explicit migration notes.

### Phase 3 — Script taxonomy
- Move one script family at a time.
- Add compatibility wrappers if existing runbooks depend on old paths.
- Keep operational scripts out of offline CI unless fully mocked and proven not to initialize MT5.

Exit: command inventory and test/CI references are updated; behavior and evidence remain unchanged.

### Phase 4 — Evidence/data boundary
- Resolve capture producer and artifact-to-observation contract from authoritative source.
- Only then implement any binding schema or producer changes.
- Verify immutable raw inputs and manifests; distinguish exact-byte verification from provenance/completeness.

Exit: contract is source-confirmed or explicitly user-approved; synthetic fixtures cover success, empty, error, partial, duplicate, and interrupted cases as applicable to the approved contract.

### Phase 5 — Multi-account selective integration
- Port small, independently tested contract slices.
- Keep account isolation and recovery fail-closed.
- No live account connection during integration tests.
- Keep Fati-specific TP/SL and notification policy separate from the primary account runner.

Exit: synthetic tests pass and account isolation is demonstrated without MT5/broker access.

### Phase 6 — Documentation and deprecation
- Build current docs index.
- Mark historical records as active, superseded, archived, or unresolved; do not rewrite conclusions.
- Deprecate only after the policy in section 8 is satisfied.

Exit: each active subsystem has one current entrypoint, one owner, and one authoritative contract index.

## 10. Required validation

Every implementation PR must include:
- exact base/head commit and changed-path inventory;
- explicit research_only=true and canonical=false where relevant;
- proof no MT5/broker access occurred for offline tasks;
- targeted tests plus full relevant regression suite;
- immutable evidence manifest/hash checks for moved or copied evidence;
- before/after import and CLI compatibility report;
- explicit statement that no active Runner or live configuration was modified.

Statistical validation remains separate from architecture refactoring. No refactor result is evidence of a trading edge.

## 11. Immediate next actions

1. Finish the complete path/import/entrypoint/CI inventory on the selected architecture branch.
2. Inspect the complete Factory module graph and existing tests before deciding exact MERGE candidates.
3. Audit the multi-account branch contract-by-contract; do not merge it wholesale.
4. Locate the actual history capture producer or authoritative capture specification. This is the current blocker for artifact-to-observation binding.
5. Present a file-level KEEP / MERGE / RELOCATE / DEPRECATE-CANDIDATE / BLOCKED matrix for user review before any code movement.

## 12. Decision log

| Decision | Status |
|---|---|
| Use StarNet integration branch as the planning baseline | Provisional working choice only |
| Treat StarNet as optional presentation, not Factory core | Proposed |
| Preserve Research Core and Forward Operations separation | Proposed architectural invariant |
| Merge multi-account branch wholesale | Rejected |
| Delete historical scripts, tests, docs, artifacts, or branches | Not authorized |
| Modify active V3.1 Runner or live config | Not authorized |
| Canonicalize unresolved Strategy A geometry | Not authorized |
| Define artifact binding contract without source/user decision | Blocked |

---
This plan intentionally prefers an explicit blocker over an invented interface or unsafe cleanup.
