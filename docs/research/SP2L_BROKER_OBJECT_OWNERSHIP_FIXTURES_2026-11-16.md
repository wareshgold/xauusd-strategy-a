# SP2L Broker Object Ownership & Linkage Fixtures — 2026-11-16

**Status:** offline research contract; non-canonical; no MT5 connection or broker actions.

## Source-aligned audit

Reviewed source on branch `research/multi-account-foundation-rfc-20261116`:

| Source | Blob SHA | Relevant behavior |
|---|---|---|
| `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py` | `7cd57892de63773db24809cb98bedba93df8f5f0` | Gateway sets symbol/magic before execute; state stores order, position, deal tickets; lifecycle and history correlate explicit broker IDs. |
| `scripts/run_sp2l_v3_1_xauusd_forward_test.py` | `c88f77d7ed19098324ecf197f732b3cb26139cfc` | V3.1 startup recovery queries active orders/positions; lifecycle filters symbol + magic; state remains runner/worktree scoped. |
| `scripts/sp2l_v31_startup_recovery.py` | `e8e501d5a7e192f512e2e9522f7e7f90bad29a28` | Startup recovery classifies active objects by exact symbol + magic and fails on unavailable inventory/invalid owned ticket. |
| `scripts/live_mt5_gateway.py` | `062ff1bdf22676f1a11f32ba90df5acdac3a802f` | Pending request carries configured magic; exposure count filters symbol query by magic. |

### Confirmed boundaries and risks

1. The audited runner process has one MT5 connection lifecycle. The account context is process/session-wide; the MT5 order, position, and deal records themselves do not carry the internal `account_key` namespace used by this research design.
2. Existing V3.1 active inventory recovery requires exact symbol + magic, but the resulting state stores bare integer tickets in separate sets. That is safe only inside the already isolated runner/account context; it is insufficient as a cross-account persistence key.
3. Existing legacy lifecycle paths can allow a previously tracked order ticket to bypass a magic mismatch check. A new multi-account worker must never let a tracked ticket override failed account identity, symbol, or magic ownership checks.
4. Source reads explicit relationship fields including order `position_id`, deal `order`, and deal `position_id`. This research contract checks only that an explicit supplied reference matches one unique target in the same verified account/symbol/magic scope.
5. Source-level references do not settle broker fill semantics, whether a pending order's position link is populated at every lifecycle stage, partial fills, netting/hedging behavior, or whether a given deal opens/closes a position. Those remain unresolved and are not encoded here.
6. Current runner startup recovery uses active orders/positions and does not prove account identity independently. The account identity contract from the previous step remains a prerequisite before any inventory may be trusted.

## Contract added

`scripts/sp2l_broker_object_ownership_contract_research.py` is pure Python. It introduces:

- Account-scoped object references: `accounts/{account_key}/{kind}/{ticket}`.
- Ownership classification requiring verified account context, exact account namespace, valid ticket, exact symbol, and exact magic.
- Missing identity/object fields fail closed; explicit symbol or magic mismatch is foreign.
- Tracked ticket presence never overrides an ownership mismatch.
- Explicit link checks for only the source-observed fields `order.position_id`, `deal.order`, and `deal.position_id`.
- Missing target references remain unresolved; conflicting/duplicate target observations are ambiguous or halt.
- No inference from timestamps, comments, magic alone, ticket proximity, or assumed fill lifecycle.

## Synthetic tests

`tests/test_sp2l_broker_object_ownership_contract_research.py` covers ownership, namespace collisions, invalid/missing fields, explicit link validation, unresolved references, mismatches, duplicate targets, and unverified identity.

Run from the multi-account worktree:

```powershell
& 'D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe' -m unittest discover -s tests -p 'test_sp2l_broker_object_ownership_contract_research.py' -v
```

## Limits / next gate

Passing these tests validates only a deterministic pure-Python contract against synthetic observations. It does not validate MT5 account identity extraction, terminal/process isolation, actual broker field availability, order/deal/position linkage, partial fills, hedging/netting behavior, durable persistence, or worker execution.

Before a worker skeleton is considered, next source-resolution tasks are to document broker/account mode assumptions from authoritative MT5 sources and design mocked adapter fixtures for incomplete/failed inventory snapshots. No live/demo connection experiment is authorized by this document.
