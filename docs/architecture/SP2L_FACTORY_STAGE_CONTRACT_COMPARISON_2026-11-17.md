# SP2L Factory Stage Contract Comparison — 2026-11-17

## Status and scope

- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/architecture-consolidation-plan-20261117`
- Source snapshot inspected: `ab26ffb61f681172bd116171ac3fc977b31dcaab`
- Scope: static comparison of `stability_factory.py`, `robustness_factory.py`, `validation_factory.py`, `holdout_factory.py`, plus their shared runner, adapter, handoff and record contracts.
- No code was executed; no tests were run; no MT5, broker, forward runner, or local worktree was accessed.
- This is a research-only architecture assessment. It does not authorize code changes or define Strategy A rules.

## 1. Shared structural pattern

All four stage factories expose:
- a stage-specific exception class;
- an immutable dataclass context;
- a result dataclass wrapping a `ResearchJobSpec` and `ResearchJobRunResult`;
- a factory initialized with an injected `ResearchJobRunner`;
- a `prepare_and_run(context)` entrypoint.

All four validate the declared test spec, readiness snapshot, handoff, source research record and source job event before preparing a job. The factories bind dataset identity using an artifact ID and content SHA-256, and delegate execution to the generic runner and an injected execution adapter where appropriate.

This common shape is a candidate for shared *internal mechanics*, not proof that stage-specific factories should be merged.

## 2. Stage-specific contract differences

| Dimension | Stability | Robustness | Untouched Validation | Fresh Holdout |
|---|---|---|---|---|
| Upstream stage | Discovery | Stability | Stability | Robustness |
| Destination station | `stability` | `robustness` | `validation` | `holdout` |
| Dataset role check | No explicit role check visible in inspected opening | No explicit role check visible in inspected opening | Requires `UNTOUCHED_VALIDATION` | Requires `FRESH_HOLDOUT` |
| Dataset immutable check | Artifact bytes are verified; no explicit `spec.dataset.immutable` check visible in inspected opening | Artifact bytes are verified; no explicit `spec.dataset.immutable` check visible in inspected opening | Explicitly requires immutable dataset | Explicitly requires immutable dataset |
| Upstream dataset reuse | Requires handoff SHA and artifact ID to match the input | Requires Stability handoff SHA and artifact ID to match the input | Explicitly rejects same dataset SHA and artifact ID as upstream Stability dataset | Explicitly rejects same dataset SHA and artifact ID as upstream Robustness dataset |
| Adapter | Constructs/uses `StabilityMatrixAdapter` and stage script context | Injected `ExecutionAdapter` | Injected `ExecutionAdapter` | Injected `ExecutionAdapter` |
| Frozen strategy revision | Not explicit in inspected context | Not explicit in inspected context | Not explicit in inspected context | Explicit caller assertion `strategy_revision_frozen`, default true, then checks upstream record identity |
| Purpose default | `STABILITY` | `ROBUSTNESS` | `UNTOUCHED_VALIDATION` | `FRESH_HOLDOUT` |
| Result payload | Job + run result | Job + run result | Job + run result | Job + run result + holdout dataset SHA |

Note: “not explicit in inspected opening” is deliberately not a claim that no equivalent validation exists later in the file. The complete method body and its tests must be checked before treating any absence as a defect.

## 3. Exact public surface observed

| Module | Context | Result | Entrypoint |
|---|---|---|---|
| `stability_factory.py` | `StabilityFactoryContext` | `StabilityFactoryResult` | `StabilityFactory.prepare_and_run` |
| `robustness_factory.py` | `RobustnessFactoryContext` | `RobustnessFactoryResult` | `RobustnessFactory.prepare_and_run` |
| `validation_factory.py` | `ValidationFactoryContext` | `ValidationFactoryResult` | `ValidationFactory.prepare_and_run` |
| `holdout_factory.py` | `HoldoutFactoryContext` | `HoldoutFactoryResult` | `HoldoutFactory.prepare_and_run` |

## 4. Shared helper extraction: candidate only

Potential common mechanics, subject to a line-by-line comparison of the complete methods and tests:
1. Validate common context objects.
2. Validate evidence-bound handoff against source record and source event.
3. Resolve and verify the declared artifact path, byte length and SHA-256.
4. Register the immutable dataset artifact with the run registry.
5. Construct the generic research job from the test specification.
6. Execute through the injected runner and adapter.
7. Record and return the stage result.

These steps are not yet approved for extraction. Differences in dataset role, source/destination station, dataset independence, frozen strategy identity, adapter construction, evidence IDs, purpose labels and result payload must remain explicit.

If a helper is later introduced, it should be a private implementation utility. The four public stage classes, contexts, results, stage-specific guards and tests should remain distinct.

## 5. Additional boundaries confirmed

- `ExecutionAdapter` is a protocol; generic execution is intentionally injected.
- `DiscoveryMatrixAdapter` and `StabilityMatrixAdapter` both invoke subprocess-backed matrix execution. They are not interchangeable merely because both implement execution receipts.
- `MT5M1ArtifactExporter` is used in the Discovery acquisition path. Discovery is not guaranteed offline.
- `ResearchHandoff` binds stage transitions and evidence to a source event and dataset identity.
- `ResearchRecord` is a separate run record/fingerprint contract; it should not be collapsed into the handoff or event journal.
- `ResearchJobSpec` validates/fingerprints the execution job and remains distinct from stage context.
- `ResearchJobRunner`, `FactoryOrchestrator`, `FactoryWorker` and `FactoryJobEventLedger` remain separate responsibilities.

## 6. Disposition

| Component | Disposition | Reason |
|---|---|---|
| Four stage factories | KEEP separate | Stage semantics and gates differ |
| Shared private helper | REVIEW / candidate | Common mechanics exist, but no equivalence proof yet |
| Stage-specific contexts/results | KEEP | Explicit contracts are useful and non-identical |
| Generic runner | KEEP | Shared execution lifecycle |
| Execution adapters | KEEP separate | Discovery and Stability have distinct invocation/validation details |
| Handoff, research record, job event | KEEP separate | Different identities and assurance roles |
| MT5 exporter and Discovery launch chain | BLOCKED | Operational acquisition boundary |
| Forward runtime adapter | BLOCKED | Can spawn a forward runner |

No files were merged, moved, deprecated or deleted.

## 7. Validation required before any implementation

A future helper extraction proposal must:
- compare every statement and branch in the four complete `prepare_and_run` methods;
- compare all four stage test modules, including negative tests and fixtures;
- prove unchanged stage-specific errors, guards, job fields, adapter arguments, evidence linkage and output shapes;
- add contract-equivalence tests for each stage;
- preserve the four public APIs and stage identity;
- run the focused test set in an isolated research environment only after explicit implementation approval;
- remain entirely separate from MT5/Forward Ops.

## 8. Phase 0 status

Phase 0 remains OPEN. This comparison narrows a possible future consolidation target but does not close the importer/entrypoint inventory. The full 90-module × script/test/workflow reference matrix is still incomplete, and no dead-code or deletion conclusion is justified.
