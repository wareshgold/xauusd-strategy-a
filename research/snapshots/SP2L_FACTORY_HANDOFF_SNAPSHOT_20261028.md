# SP2L Strategy Research Factory — Handoff Snapshot

- Snapshot ID: `SP2L-FACTORY-HANDOFF-20261028`
- Recorded: 2026-10-28
- Repository: `wareshgold/xauusd-strategy-a`
- Intended work area: `research/factory-candidate-lab-20261010`
- Branch tip observed through PR #353 base: `8471b175f71e3af650babe52720d5a163a0bb61d`
- Related current Factory PRs:
  - [#352 — quarantine historical runtime journal evidence](https://github.com/wareshgold/xauusd-strategy-a/pull/352), Draft/open, head `ffb22153cfe2a04d10e547101971116d0333315d`.
  - [#353 — tick gate and synthetic fixture contract](https://github.com/wareshgold/xauusd-strategy-a/pull/353), Draft/open, head `9d6ee131075101179c2b45cb4fd78ac0491b5c2f`.
  - [#348 — journal-isolation test in CI](https://github.com/wareshgold/xauusd-strategy-a/pull/348), merged 2026-10-25; its CI additions are present in the Factory workflow.
  - [#334 — persisted Factory lifecycle append guard](https://github.com/wareshgold/xauusd-strategy-a/pull/334), open, not merged.
- This is a research handoff, not a strategy freeze or production approval.

## User's actual objective

Continue building and verifying the SP2L Strategy Research Factory / StarNet research workflow. The recent detour into position 64500649 trailing diagnostics was ancillary and is **not** the primary workstream. Do not keep advancing that incident unless the user explicitly redirects back to it.

The goal is a source-aligned, deterministic, statistically validated XAUUSD Strategy A process. Prove provenance, lifecycle integrity, data readiness, validation boundaries, and reproducibility before any production consideration.

## Governing workflow

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Factory lifecycle framing used in recent work:

`DISCOVERY → FROZEN STRATEGY → VALIDATION → ROBUSTNESS/STABILITY → HOLDOUT → FORWARD GATE → DEMO FORWARD → RECONCILIATION`

The Factory is research infrastructure; it must not silently become a production signal generator.

## Confirmed branch/CI facts at snapshot time

### Factory branch base

Commit `8471b175f71e3af650babe52720d5a163a0bb61d` — `Make Factory orchestrator journal safe by default (#351)`.

The commit changes implicit FactoryOrchestrator construction to use an in-memory journal (`path=None`) and adds a regression test plus CI coverage. Both workflows passed on this commit:
- Factory Research Tests — run 807 — success.
- SP2L forensic deterministic checks — run 465 — success.

### PR #353 tick-gate and synthetic-fixture branch

Head `9d6ee131075101179c2b45cb4fd78ac0491b5c2f`. Both workflows passed on this PR head:
- Factory Research Tests — run 1040 — success.
- SP2L forensic deterministic checks — run 578 — success.

The PR includes a broad set of synthetic fixtures, source execution preflight diagnostics, conservative order/deal/position reconciliation, evidence graph/planner, and append-only hash-chained experiment ledger. These are deterministic research components; passing synthetic tests is not proof of live broker semantics, full-history coverage, or statistical edge.

Open review checklist on #353 still includes:
- Review the provisional 2026-09-07 session-calendar assumption.
- Review the fail-closed gateway patch before any merge or runner adoption.
- Confirm CI on the latest head before treating it as current.
- Review graph/reconciliation/ledger invariants; canonical and production authorization must remain false.
- Resolve execution semantics against source and broker evidence; theoretical levels do not prove fills.

### PR #352 journal-quarantine disposition

Head `ffb22153cfe2a04d10e547101971116d0333315d`. Both workflows passed:
- SP2L forensic deterministic checks — run 466 — success.
- Factory Research Tests — run 808 — success.

It documents the historical runtime journal anomaly and explicitly preserves uncertainty about the writer. It must not be auto-repaired, truncated, replayed, or rewritten.

### Existing journal-isolation CI

PR #348 merged on 2026-10-25. The current Factory workflow includes `tests/test_factory_test_journal_isolation.py` and `tests/test_factory_orchestrator_default_journal_isolation.py`. The merged workflow at the branch base runs the expanded focused Factory suite.

## Critical known blocker: historical Factory journal evidence

The inspected local Factory runtime journal was structurally valid JSONL but had repeated `COMPLETED` lifecycle events for `DISCOVERY-1`. This is a lifecycle-integrity conflict, not merely a JSON syntax problem.

Required treatment:
- Keep the original runtime journal and all evidence intact.
- Do not truncate, rewrite, replay, auto-repair, or infer that the journal is trustworthy because its JSON parses.
- The safe-default and append-guard changes prevent classes of future invalid writes; they do not identify the historical writer or resolve the existing anomaly.
- Reconcile only through a non-mutating, provenance-preserving procedure with explicit evidence and human review.
- Do not claim the local runtime journal has been repaired or that its lifecycle history is authoritative.

## Critical data/semantic blockers

- Raw Tick Bid/Ask dataset for the historical comparison interval was previously marked **NOT YET ACQUIRED** in the Candidate Lab evidence. Required interval: `[2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)`, symbol `XAUUSD.ecn`, server `OtetGroup-MT5`. Confirm current local acquisition state before making any claim; GitHub cannot see the user's local MT5 history.
- Fresh Holdout boundary beginning `2026-09-19` must remain excluded from candidate tuning.
- M1 OHLC must not be silently substituted for tick Bid/Ask or described as exact execution parity.
- Partial-fill reconciliation, event timing/order, fill/cost semantics, trailing outcomes, 2X lifecycle, candle construction, and immutable dataset binding were listed as blockers before honest historical replay.
- Source geometry remains unresolved wherever source evidence does not decide it. Do not invent P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.

## Next task for the receiving chat

**Resume the Factory workstream first, not the trailing incident.** Work GitHub-first and stay on `research/factory-candidate-lab-20261010`.

1. Reconcile the current remote branch tip and PR #352/#353 state, then check CI on each current head. Do not assume the SHAs in this snapshot are still latest.
2. Inspect the exact code/tests/docs around the Factory lifecycle journal, the read-only quarantine disposition, and the #353 tick-gate/fixture contract. Identify any remaining gap between synthetic test coverage and the actual Factory readiness gates.
3. Prioritize a deterministic, non-mutating audit/reconciliation path for the historical journal anomaly. Preserve source bytes and hashes; emit separate new reports/snapshots with explicit evidence status and unresolved contradictions. Never modify the original journal.
4. Verify that the Factory end-to-end readiness path enforces identity/provenance across `Fresh Holdout → Handoff → Gate → Session → Lifecycle`, plus immutable dataset/code/strategy identity and explicit production-disabled state.
5. Record an additive snapshot after each meaningful milestone and run the relevant CI. Distinguish tested code commit from later documentation-only snapshot commits.
6. Only after the evidence/lifecycle gates are trustworthy should the work proceed to clean, untouched validation/robustness/Fresh Holdout readiness. Do not run a new backtest or tune parameters until source and dataset prerequisites are resolved.

## Strict operating constraints

- Work only in `research/factory-candidate-lab-20261010` for this task.
- Leave `main`, unrelated branches, other worktrees, the Strategy A RR2/TRAIL4 forward test, Strategy B forward test, MT5 session/account, runtime state, event logs, and local evidence untouched.
- Never use `git reset`, `git clean`, force-push, mass-stage, mass-delete, or overwrite modified/untracked evidence.
- Do not merge Draft PRs unless the user explicitly authorizes it.
- Do not issue production BUY/SELL decisions; production authority stays disabled.
- Source meaning outranks backtest performance. Diagnostics are not canonical rules.
- AI may assist research, engineering, validation, documentation, and analytics, but cannot autonomously define canonical SP2L rules or produce production trading decisions.
- User expects exact, concise, paste-ready PowerShell only when a local check is actually required; prefer output copied directly to Clipboard. Never ask the user to paste huge logs if a concise filtered report can be generated.

## Important prior context

- Factory branch was previously reported locally as `research/factory-candidate-lab-20261010`, with a local worktree at `D:\Mirzaei\Private\1\xauusd-strategy-a-factory-candidate-lab`; earlier HEAD was `cd48a52b`. This is historical context, not confirmation of current local HEAD. Verify read-only before any local work.
- A prior snapshot PR (#339) documented a local-vs-remote Factory HEAD reconciliation warning. Do not assume local and remote tips match.
- The user specifically corrected the recent detour: their main request is Factory/StarNet progress with snapshots, not continued focus on the single trailing incident.

## Handoff success criteria

A successful next session should be able to state, with evidence:
1. Current Factory branch/PR/CI state.
2. Exact remaining journal-integrity gap and a safe, non-mutating reconciliation plan.
3. Exact end-to-end readiness gate failures or missing evidence, without inventing missing facts.
4. Next bounded change, tests, snapshot, and CI plan.
5. Confirmation that no live runner, MT5 state, forward-test evidence, or canonical strategy rules were changed.
