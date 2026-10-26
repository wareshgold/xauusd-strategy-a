# Factory Research Snapshot — 2026-10-26

## Snapshot identity

- Repository: `wareshgold/xauusd-strategy-a`
- Research branch: `research/factory-tick-gate-fixtures-20261026`
- Snapshot recorded at commit: `86d6cb95e3806c8b093d837d7f01445edeea7dd1` (pre-step baseline)
- Snapshot purpose: preserve the exact research state before the next Evidence Graph / experiment-planning increment.
- PR: [#353](https://github.com/wareshgold/xauusd-strategy-a/pull/353), OPEN, DRAFT, unmerged.
- Base branch: `research/factory-candidate-lab-20261010`
- Baseline CI: Factory Research Tests SUCCESS [run 40291596516](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40291596516); SP2L forensic deterministic checks SUCCESS [run 40291596571](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40291596571).

## Preserved work

- Tick dataset identity, timestamp duplicates/gaps, and provisional 2026-09-07 session-calendar assumption.
- Deterministic synthetic tick/order-sensitive fixtures.
- Research-only source execution preflight fixtures.
- Narrow fail-closed pending-order verification patch on this unmerged branch.
- Source-order lifecycle classification and Order/Deal/Position reconciliation fixtures.
- Lifecycle event timeline audit.
- Observed Deal economic ledger arithmetic.
- History query failure versus successful empty observation and delayed-appearance fixtures.
- Research Brain policy gate: explicit evidence roles/hashes; contradictions, failed tests, missing source evidence, and inconclusive evidence block promotion; canonical and production authorizations hard-false.

## Boundaries

- Snapshot is a GitHub research record, not a local disk/worktree archive and not a broker-account snapshot.
- No local files, local worktrees, MT5 session/account, live runner, or Strategy A forward-test artifacts were modified.
- No Strategy B run, historical replay, or performance backtest was performed.
- No PR merge or production deployment was performed.
- Synthetic CI passing does not prove live broker behavior, complete history, canonical SP2L geometry, or statistical edge.
- Replay remains blocked on unresolved execution, fill/partial-fill, cost, event ordering, trailing, 2X lifecycle, candle-construction, and immutable data-binding questions.

## Follow-up increment later on 2026-10-26

- Evidence Graph and deterministic research-action planner were added in commit 26394e883e769f7b4057c047e42bdfe048636ef3.
- Follow-up commit `0128e1f0e7d7b090d9b9921ffef3b13c34adf733` adds adversarial reconciliation fixtures for duplicate order/position identities and stricter graph role/outcome/relation validation.
- Latest verified checkpoint at snapshot refresh: `0128e1f0e7d7b090d9b9921ffef3b13c34adf733`; both focused CI workflows succeeded (runs 40293637746 and 40293637776).
- The baseline commit above remains the original snapshot point; the current branch head and its CI runs define the latest state.

## Added audit record

- `docs/research/RECONCILIATION_COUNTEREXAMPLE_AUDIT_2026-10-26.md` records the duplicate-identity counterexamples and explicitly scopes the tests as synthetic structural checks.

## Experiment ledger increment completed

- Ledger implementation: `src/strategy_factory/research_ledger.py`.
- Focused tests: `tests/test_strategy_factory_research_ledger.py`.
- Contract: `docs/research/FACTORY_RESEARCH_EXPERIMENT_LEDGER_CONTRACT_2026-10-26.md`.
- Implementation commit: `1022d1a3721a421ecaa181fdcec7abdc6fe0bf94`.
- CI workflow continuation fix: `942d0f7de494c228be444417ab4ac8b2090fb275`.
- Both workflows passed on the fixed commit: Factory Research Tests [run 40295014150](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40295014150); SP2L forensic deterministic checks [run 40295014134](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40295014134).
- The ledger does not contain fabricated historical or trading outcomes; no experiment was run as part of this increment.


## Experiment planner/registry increment — 2026-10-26

- Planner: `src/strategy_factory/experiment_planner.py`.
- Tests: `tests/test_strategy_factory_experiment_planner.py`.
- Contract: `docs/research/FACTORY_EXPERIMENT_PLANNER_REGISTRY_CONTRACT_2026-10-26.md`.
- Added stable IDs for three evidence-handling research questions and three existing synthetic test cases: same-millisecond tick order, OHLC SL/TP double-touch ambiguity, and explicit completed-bar gating. These are not hypotheses about canonical SP2L trading geometry.
- `plan_experiments` emits deterministic `PLANNED` records only, binding caller-supplied input/code hashes and the prior record hash. Unknown/duplicate IDs and dangling registry references fail closed.
- Planned records explicitly state “not executed”; no PASS/FAIL outcomes were fabricated. No actual experiment was run by this increment.
- The new planner tests are included in Factory Research Tests CI. CI must be checked on the final branch head before treating this increment as verified.
- No local files/worktrees, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No PR merge or production deployment.


## Captured execution-result ingestion increment — 2026-10-26

- Ingestion boundary: `src/strategy_factory/execution_result_ingestion.py`.
- Tests: `tests/test_strategy_factory_execution_result_ingestion.py`.
- Contract: `docs/research/FACTORY_EXECUTION_RESULT_INGESTION_CONTRACT_2026-10-26.md`.
- The boundary accepts caller-supplied run ID, command, exit code, output/environment SHA-256 hashes, evidence refs, and result summary; it creates a result record only when linked to a valid `PLANNED` record with the exact prior hash.
- Zero exit code maps to PASS and nonzero to FAIL for the captured test process only. Evidence hashes are format-validated and included in record provenance. Missing refs, invalid hashes, wrong prior hashes, or non-PLANNED source records fail closed.
- Important limitation: ingestion validates supplied metadata; it does not run the command, fetch/authenticate CI artifacts, or prove that the claimed execution occurred. Actual output bytes must be preserved and independently hashed by the caller. No captured execution report was ingested in this increment.
- New tests were added to Factory Research Tests CI; verify results on the final branch head before considering the increment checked.
- No local worktrees/files, MT5 session/account, live runner, Strategy A forward-test artifacts, or Strategy B run were touched. No historical replay, merge, or production deployment.

## Next increment

Add a read-only report builder that checks a full ordered ledger against a separately supplied pinned tip/count and summarizes PLANNED versus captured outcomes, failures, counterexamples, and evidence gaps without upgrading source status or canonical authority. Do not treat caller-supplied execution metadata as independently authenticated.
