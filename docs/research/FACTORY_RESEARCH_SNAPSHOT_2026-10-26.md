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

## Next increment

Implement a versioned, append-only experiment ledger binding hypothesis version, frozen input hash, code hash, result, evidence status, counterexamples, and prior failures. Pin its expected tip/count externally when using it to detect truncation.
