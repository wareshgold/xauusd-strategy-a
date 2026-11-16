# SP2L Multi-Account Foundation — Research RFC

**Status:** Draft / research-only / non-canonical  
**Date:** 2026-11-16  
**Scope:** Architecture proposal only. No trading logic, canonical SP2L geometry, production execution policy, or live-account activation is approved by this document.

## 1. Safety boundary

- The currently running V3.1 XAUUSD Runner is out of scope and must remain unchanged.
- All development takes place on this research branch or isolated worktrees.
- No additional account may submit orders during architecture, fixture, unit-test, integration-test, or shadow-mode stages.
- No production BUY/SELL decisions are delegated to AI.
- Existing source-confirmed SP2L rules remain authoritative. Unresolved P-Gap, AB=CD, fill, and execution semantics must not be inferred or filled in by this work.
- Any future account activation requires explicit operator approval after validation.

## 2. Proposed architecture (not yet approved)

Separate the shared signal/entry population from account-specific execution and trade-management policies:

1. **Entry population interface** — immutable, versioned candidate records from an approved upstream source. The interface transports facts; it does not reinterpret SP2L geometry.
2. **Account worker** — one isolated runtime boundary per account/terminal session. It owns that account's broker connection, reconciliation, order lifecycle, state, logs, and recovery.
3. **Account policy adapter** — explicitly selected management policy for the account. Policies must not share mutable state.
4. **Account risk guard** — account-scoped limits and fail-closed checks before any future execution.
5. **Read-only observer** — consumes worker-produced files/snapshots; it never attaches to the trading terminal or sends broker requests.

The exact MT5 multi-terminal/process topology must be verified experimentally before implementation. Do not assume that multiple account sessions can safely share one Python MT5 IPC connection or one terminal process.

## 3. Account isolation requirements

Every account must have independently namespaced:

- broker identity fingerprint (broker/server/login identifier; never store passwords or secrets in logs);
- terminal/process identity and connection health;
- symbol mapping and broker contract metadata;
- magic-number range and order/position ownership;
- runtime state, lock, recovery journal, event stream, and evidence manifest;
- execution policy and policy version;
- risk limits and operator enable/disable state;
- Telegram routing and notification policy.

A worker must fail closed if the connected broker/server/login does not match its configured identity. An account worker must never manage orders or positions owned by another account or another strategy/magic namespace.

## 4. First secondary-account research candidate: Fati

Prior operator direction to preserve as constraints for research:

- Fati is a separate account with its own trade-management policy.
- Fati's management component owns TP decisions/management; the initial SL remains fixed.
- No trailing-SL behavior and no reuse of the primary Runner's trailing logic for Fati.
- Fati notifications are limited to Pending Order and Order Filled events routed to Fati's private destination; do not route Fati trade outcomes/results there.
- The exact TP algorithm/parameters are not specified by this RFC.
- Break-even behavior remains unresolved and must not be implemented until explicitly reconciled with the fixed-initial-SL decision.

These are account-specific design constraints, not permission to connect or trade the Fati account.

## 5. Fail-closed and restart-safety requirements

Before any demo execution is considered, fixtures must cover:

- broker identity mismatch;
- missing, corrupt, stale, or schema-incompatible account state;
- ambiguous ownership of broker orders/positions;
- duplicate candidate delivery and duplicate order submission;
- process restart with pending orders and open positions;
- partial/unknown broker responses and history-query failures;
- rejected modifications and invalid broker stop distances;
- account isolation (an event or position from account A cannot mutate account B);
- notification routing and duplicate suppression;
- manual disable / emergency stop behavior.

Unknown or ambiguous recovery state must stop that account worker rather than guess.

## 6. Risk controls to research

Potential account-scoped controls (thresholds must be supplied/approved by the operator, not invented here):

- maximum open positions and pending orders;
- maximum exposure/volume;
- daily loss and drawdown limits;
- maximum consecutive execution failures;
- stale tick / stale data guard;
- spread and market-condition guard, only where definitions are source-confirmed;
- explicit per-account enable flag and independent emergency stop.

No default numeric thresholds are defined by this RFC.

## 7. Operator dashboard direction

The dashboard remains a read-only filesystem observer. It should be redesigned as a compact engineering instrument panel, not a dense trading cockpit:

- a small top strip for Runner/worker health and data freshness;
- one primary capital-performance plot;
- a compact drawdown/risk summary;
- a narrow recent-events table;
- diagnostics and per-account details in collapsed secondary sections.

Capital metrics must carry provenance and account currency. Equity must not be inferred from event-reported net P/L. A trustworthy equity curve requires reconciled account snapshots/history or another verified source. If the source is unavailable, display “not available” rather than fabricated or estimated values.

## 8. Delivery workflow

1. Source and current-code audit.
2. Synthetic account-isolation and recovery fixtures.
3. Freeze interface contracts (not SP2L geometry).
4. Implement research-only account worker skeleton and policy adapter.
5. Unit/integration tests with mocked broker boundary.
6. Demo-terminal isolation test with no order submission.
7. Shadow mode and evidence capture.
8. Independent validation and operator review.
9. Fresh holdout / production consideration only after explicit approval.

## 9. Immediate next engineering tasks

- Audit the current V3.1 runner's MT5 lifecycle, state schema, order ownership, and recovery boundary without modifying the running worktree.
- Locate existing Fati research modules and tests; map what can be reused without importing primary trailing behavior.
- Write synthetic fixtures for account identity, state isolation, duplicate delivery, and restart recovery.
- Audit the dashboard's current event/state schema and define a provenance-bearing capital snapshot contract before adding an equity chart.

**Non-goals:** modifying the active Runner, connecting another account, placing orders, changing SL/TP, choosing unresolved strategy geometry, or promoting research behavior to canonical/production.
