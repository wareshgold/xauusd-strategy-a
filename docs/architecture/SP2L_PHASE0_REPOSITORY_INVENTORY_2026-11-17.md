# SP2L Phase 0 — Repository Inventory (Initial Static Pass) — 2026-11-17

## Status

- Scope: GitHub repository static inventory only
- Branch inspected: `research/architecture-consolidation-plan-20261117`
- Planning base: `research/sp2l-starnet-engine-integration-20261007` at `befec09c752e8d7ba9d10ff75d4e39ad5351c853`
- Inventory commit: `ad468f6d544609d291139de630ba73d37d06a0e7` (initial creation; this metadata correction is a subsequent commit)
- Runtime code executed: NO
- Tests executed: NO
- MT5/broker/terminal accessed: NO
- Local dirty worktree touched: NO
- Source geometry or canonical rules changed: NO
- Evidence/data deleted or rewritten: NO

This is an initial static inventory, not a complete import/dependency graph. File classifications are provisional. No deletion, move, merge, deprecation, or branch cleanup is authorized by this report.

## 1. Repository tree snapshot

GitHub recursive tree for the inspected planning commit returned 970 tree entries, 916 blobs, 54 tree entries, and was not truncated.

| Area | Files observed | Initial interpretation |
|---|---:|---|
| `src/` | 131 | Mixed TypeScript domain/backtest/execution and Python Factory |
| `src/strategy_factory/` | 90 | Large Python research orchestration/evidence subsystem |
| `scripts/` | 174 | Mixed research, acquisition, backtest, forensic, Factory, and live/forward entrypoints |
| `tests/` | 139 | 109 Python, 29 TypeScript/JavaScript, plus placeholder |
| `docs/` | 279 | 251 under `docs/research/`, plus other docs |
| `artifacts/` | 92 | Historical results, reports, forensic and forward evidence |
| `data/` | 50 | Historical datasets, MT5 acquisitions, session availability, reports |
| `research/` | 22 | Research snapshots, engine helpers, fixtures and harness |
| `.github/workflows/` | 8 | CI, research workflows and some write-capable workflows |
| `runtime/` | 5 | Examples and MT5 MCP read-only benchmark/inspection scripts |
| `MQL5/` | 1 | One MT5 Expert Advisor source |

Counts are path counts in this inspected Git tree. They are not counts of active/used modules. The `src/strategy_factory/` count is included within `src/`; other directory totals are likewise not additive to the repository total.

## 2. Root-level build and test surfaces

### Node / TypeScript

`package.json` exposes:
- `build`: `tsc --noEmit`
- `test`: `vitest run`
- `lint`: `eslint .`
- `download:data`: Twelve Data downloader
- `audit:data`: dataset audit
- `backtest:baseline`: TypeScript baseline backtest

Node engine is declared as >=22. The main `tsconfig.json` includes all of `src` and `tests`, so the TypeScript project currently includes strategy/domain, backtest, execution, and test code together.

A separate `tsconfig.sp2l-harness.json` includes an explicit subset of `research/harness` and SP2L tests. This creates two TypeScript validation surfaces that need an explicit ownership/coverage map; neither should be removed until their distinct contracts and coverage are understood.

### Python

`pyproject.toml` defines package `xauusd-strategy-a-research`, requires Python >=3.12, and discovers packages from `src`.

`pytest.ini` sets `testpaths=tests` and `pythonpath=scripts`. The Factory CI workflow separately sets `PYTHONPATH=src`. This difference must be reconciled/documented so local and CI test import behavior is reproducible. The repository currently has 109 Python test files.

There is no single root-level command in `pyproject.toml` declaring the canonical full Python test suite. The CI workflows run selected subsets rather than a single demonstrated full-suite gate.

## 3. Strategy and execution source layout

### TypeScript domain / application / infrastructure

Observed logical areas:
- `src/domain/market/`: candle, breakout, follow-through, market quality and structure.
- `src/domain/structure/`: market structure.
- `src/domain/strategy-a/`: 13 Strategy A research/domain modules, including `PGAPResearch.ts`, `SpikeDetector.ts`, `CorrectionDetector.ts`, `LegProjection.ts`, `EntryTrigger.ts`, and stop/invalidation modules.
- `src/application/market-data/`: M5 aggregation.
- `src/infrastructure/market-data/`: Twelve Data client.
- `src/backtest/`: candle/data parsers and stores, replay engine, backtest engine, Strategy A adapter.
- `src/execution/` and `src/execution/mt5/`: position/trailing safety and broker-constraint / position-modification contracts.

Source spot-checks confirm `PGAPResearch.ts` explicitly describes its three-candle imbalance as a research candidate, not a validated P-GAP definition. This is consistent with the no-invented-geometry rule. `TwoLegSetup.ts` emits a potential/rejected setup representation; it is not evidence that the complete canonical execution contract is resolved.

Initial disposition:
- KEEP the domain and backtest layers as separate research surfaces pending semantic/import audit.
- BLOCK changes to execution/MT5 modules pending explicit operational scope.
- Do not consolidate TypeScript strategy logic with Python Factory orchestration merely to reduce language count.

## 4. Python Strategy Factory module surface

There are 90 files under `src/strategy_factory/`. The package exports many modules from `__init__.py`, including datasets, runs, evidence, provenance, execution receipts, jobs, runner, orchestrator, event ledger, synthetic execution, source resolution, readiness, statistical validation, stability, and related Factory services.

The central responsibilities are not identical:
- `factory.py` + `gates.py` + `models.py`: four named gate model (Strategy Lab, Strategy Engine, Test Factory, Forward Validation).
- `runner.py`: executes one declared research job through an injected adapter and binds run/evidence/provenance/audit records.
- `orchestrator.py`: FIFO queue, worker dispatch, lifecycle events, handoffs.
- `worker.py`: worker lifecycle and telemetry publishing.
- `job_events.py`: append-only lifecycle journal.
- `starnet_adapter.py`: deterministic projection from worker/event telemetry into renderer state.
- `telemetry.py`: atomic JSON status-file publication.

Static inspection shows `runner.py` and `orchestrator.py` are complementary rather than obvious duplicates: the runner owns a validated research job execution/evidence boundary, while the orchestrator owns queue and worker lifecycle. `worker.py` is a distinct worker state machine. These should not be merged based only on similar naming.

However, `factory.py` gate names and `models.Stage` vocabulary do not directly match the required workflow labels. A controlled crosswalk is needed; do not silently change gate semantics.

Initial disposition:
- KEEP runner, orchestrator, worker, event ledger, telemetry, and renderer adapter as separate responsibility candidates.
- REVIEW the older four-gate facade and its production-eligibility property against the newer job/evidence acceptance path before deciding whether it is retained as a compatibility facade, adapted, or deprecated.
- REVIEW clusters of similarly named evidence, provenance, certification, ledger, stability, comparison, and forward modules by import and invariant ownership before any merge proposal.

## 5. Scripts inventory and entrypoint families

There are 174 files under `scripts/`. A filename-only, mutually exclusive first-pass classification (priority order: Factory, forward/live, acquisition, backtest/replay, forensic/reconciliation, other) produced:

| Filename family | Count | Initial disposition |
|---|---:|---|
| Factory / StarNet | 5 | KEEP; inspect launch/telemetry overlap |
| Forward / live / Telegram | 34 | BLOCKED from refactor pending operational boundary audit |
| Acquisition / data export | 17 | KEEP; separate online acquisition from offline transforms |
| Backtest / replay / matrix | 32 | KEEP; map to reusable engines vs historical experiment drivers |
| Forensic / reconciliation / diagnostics | 38 | KEEP pending evidence-reference audit; do not execute MT5-initializing candidates |
| Other / mixed / unclassified | 48 | REVIEW individually; filename does not establish purpose |

These buckets are lexical triage only, not verified dependency or runtime classification. A script may call MT5 even if its filename does not include MT5. No script was executed.

The Factory presentation entrypoints currently include:
- `scripts/factory_dashboard.py`
- `scripts/factory_starnet_world.py`
- `scripts/factory_demo.py`
- `scripts/bootstrap_starnet_engine.ps1`

The dashboard and StarNet world both read Factory telemetry, but their full route, endpoint, process, and asset responsibilities have not yet been compared line-by-line. They are MERGE-CANDIDATES for a single documented launch surface, not approved for code merge. The demo writer uses a separate demo telemetry path and should remain isolated.

## 6. CI and automation inventory

Eight workflows were found:

| Workflow | Trigger / scope | Initial concern |
|---|---|---|
| `factory-tests.yml` | Push to `research/**`, PR | Runs a focused list of Python Factory tests, not all 109 Python test files |
| `research-sp2l-validation-harness.yml` | Path-filtered push/PR | Runs a selected TypeScript harness subset and research backtest/diagnostic scripts |
| `research-author-replica-backtest.yml` | One historical branch push, manual dispatch | Branch-specific research runner |
| `research-baseline-forensic-audit.yml` | Manual dispatch | Checks out `main`, has `contents: write`, commits/pushes report to `main` |
| `research-dataset-refresh.yml` | Manual dispatch | Checks out phase12 branch, uses Twelve Data secret, downloads data and commits/pushes to research branch |
| `research-phase12-preentry-geometry-robustness.yml` | Manual dispatch | `contents: write`; runs analysis and commits/pushes report to a fixed research branch |
| `sp2l-forensic-checks.yml` | Branch-specific push / PR | Runs selected Python detector/reconciliation checks |
| `sp2l-forensic-telemetry.yml` | Branch/path-specific push, manual | Runs telemetry analysis |

The three workflows with explicit write permissions or commit/push behavior require careful ownership and branch-target documentation. They are not being disabled or changed in this inventory. Before consolidation, we must establish which are still intentionally used and whether manual dispatch on the current branch can produce commits on a different fixed branch.

CI coverage is currently fragmented: the Factory workflow and forensic workflow execute selected Python tests; the TypeScript harness workflow executes selected TS tests. There is no evidence in the inspected workflow files of one universal workflow that runs the full Python suite, full TypeScript build/test/lint, and all static safety checks together.

## 7. Data, artifacts, docs, and external dependency

### Data and artifacts

- `data/` has 50 tracked files, including historical OHLC datasets, MT5 acquisition CSVs and matching manifests, session availability CSV/JSON/gap outputs, and dataset audit output.
- `artifacts/` has 92 tracked files, including historical backtest matrices/reports, forensic reports, a forward events JSONL, and factory snapshot.
- These are evidence-bearing assets. No deduplication or relocation decision can be made from names or apparent content similarity alone. Any future move requires reference mapping and byte/hash preservation.

### Documentation

- `docs/research/`: 251 files.
- `docs/checkpoints/`: 17 files.
- `docs/execution/`: 3 files.
- `docs/live/`: 4 files.
- plus root live docs, strategy specification, and this architecture area.

The README says “Project foundation. Strategy implementation has not started,” while the same tree contains substantial Strategy A domain/backtest code, a large Factory, 139 tests, data, artifacts, and live/forward modules. This is a confirmed documentation drift. Update the README only after a current project status statement is agreed; do not treat the old README pipeline as an authoritative inventory.

The `docs/strategy-a.md` specification itself says exact numeric thresholds remain unresolved and P-GAP must not be invented. Preserve it and all source-resolution history.

### StarNet submodule

`.gitmodules` declares `vendor/starnet-engine` from the upstream StarNet repository and a branch name. The inspected recursive tree did not contain a `vendor/starnet-engine` gitlink or vendor tree entry. This is a repository consistency question: determine whether the submodule was intentionally removed, omitted from this branch, or the declaration is stale. Do not run bootstrap or alter submodule metadata until confirmed.

## 8. Provisional disposition matrix

| Area | Disposition | Reason / next proof |
|---|---|---|
| `src/domain/**` | KEEP | Strategy domain and market structure; preserve source ambiguity |
| `src/backtest/**` | KEEP / REVIEW | Reusable deterministic engine vs experiment-specific adapters not fully mapped |
| `src/execution/**` | BLOCKED | Operationally sensitive; no changes under Phase 0 |
| `src/strategy_factory/runner.py` | KEEP | Research job execution/evidence boundary |
| `src/strategy_factory/orchestrator.py` | KEEP | Queue and lifecycle orchestration distinct from job runner |
| `src/strategy_factory/worker.py` | KEEP | Worker lifecycle distinct from queue and execution adapter |
| `src/strategy_factory/factory.py` | REVIEW | Older four-gate facade may overlap conceptually with newer acceptance/gate flow |
| `src/strategy_factory/starnet_adapter.py` | KEEP | Renderer-neutral telemetry projection |
| Factory dashboard launchers | MERGE-CANDIDATE | One launch surface may be possible; compare server routes, telemetry inputs, and vendor dependencies |
| `scripts/*forward*`, live gateways, Telegram | BLOCKED | Active operational paths; no code or configuration changes |
| Acquisition and forensic scripts | KEEP / REVIEW | Establish whether each is live MT5 access, offline analysis, or historical one-off |
| `tests/**` | KEEP | Tests are executable contracts; map coverage before relocation |
| `docs/research/**` | KEEP / INDEX | Historical research and source-resolution records |
| `data/**`, `artifacts/**` | KEEP IMMUTABLE | Evidence/data; no dedupe by filename |
| CI workflows | REVIEW / BLOCKED | Write-capable branch automation needs owner/usage verification |
| StarNet submodule declaration | BLOCKED | Tree/config mismatch unresolved |

## 9. Phase 0 gaps — work still required

This initial static pass is not sufficient to authorize file-level MERGE or RELOCATE actions. Remaining required evidence:

1. Full import graph for Python `src/strategy_factory`, scripts, and tests, including dynamic imports and CLI references.
2. TypeScript import graph across `src/domain`, `src/backtest`, `src/execution`, `research/harness`, and tests.
3. Entry-point inventory: console commands, `if __name__ == "__main__"`, package scripts, dashboard ports, scheduled tasks/runbooks, and workflow invocations.
4. MT5 access classification for every script and adapter by static inspection only. Never run a candidate to find out.
5. Artifact/data reference graph: which scripts/tests/docs consume each evidence family; no hashing or file movement is required for this static pass.
6. Workflow ownership and actual last-use verification for write-capable workflows.
7. Submodule status reconciliation.
8. Cross-branch selective map for the multi-account foundation work; no wholesale merge.

### Phase 0 exit criteria

Phase 0 remains OPEN until each proposed move/merge has known importers, test references, CI references, runbook/CLI references, evidence references, and an explicit owner. Any unknown dependency means BLOCKED, not safe to remove.

## 10. Next safe action

Continue with a static dependency/entrypoint pass on this same GitHub branch. Start with the 90-module Factory package and the approximately 46 filename-matched Factory/research test candidates (lexical grouping only; importer relevance remains unverified), then map the four Factory/StarNet entrypoints and their telemetry files. Do not modify runtime code. Publish the resulting dependency matrix before proposing any code change.
