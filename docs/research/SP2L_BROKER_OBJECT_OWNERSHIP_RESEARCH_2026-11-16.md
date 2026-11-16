# Broker Object Ownership Contract — Offline Research

**Date:** 2026-11-16  
**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Status:** synthetic contract proposal; non-canonical; not integrated into a worker.

## Source-aligned findings

Read-only review of the V3.1 source found:

- Startup recovery in `scripts/sp2l_v31_startup_recovery.py` classifies active objects by exact symbol + magic and stores order/position ticket integers in separate state sets.
- V3.1 wrapper recovery obtains `orders_get(symbol=...)` and `positions_get(symbol=...)` from the currently connected process-level MT5 session, then calls the recovery helper.
- Pending-order lifecycle records the broker order's `position_id`; position lifecycle uses the position object's `ticket`.
- The base runner's lifecycle/history code also reads deal `position_id` and queries `positions_get(ticket=position_id)`.
- The current source does not bind those inventory observations to an independently verified expected broker/server/login identity at the ownership-helper boundary. The separate V3.1 startup guard enforces Demo mode but is not a multi-account identity binding.
- The current MT5 Python session is process-level; source review does not prove safe simultaneous sessions or terminal isolation.

This audit does **not** infer that order `position_id`, deal `position_id`, and position `ticket`/identifier are interchangeable. Their linkage semantics must be verified against authoritative MT5 documentation and broker behavior before implementing reconciliation.

## Contract added for synthetic research

`scripts/sp2l_broker_object_ownership_contract_research.py`:

1. Calls the existing exact broker/server/opaque-login-reference identity assertion before classifying inventory.
2. Scopes object keys by account key, object kind, and ticket. An order ticket and position ticket with the same numeric value remain distinct.
3. Uses exact symbol + magic only as the within-account strategy/worker filter, not as proof of account identity.
4. Ignores well-formed objects outside the requested symbol + magic scope.
5. Halts on malformed object records or conflicting duplicate keys rather than guessing.
6. Does not persist anything, connect to MT5, issue broker requests, or interpret order/position linkage.

## Synthetic fixtures

`tests/test_sp2l_broker_object_ownership_contract_research.py` covers:
- exact identity and object ownership;
- account identity mismatch even when symbol + magic match;
- foreign symbol/magic filtering;
- same numeric ticket across order and position kinds;
- duplicate observation deduplication and conflicting duplicate rejection;
- invalid ticket/scope and valid empty inventory;
- account/kind/ticket namespace separation.

## Explicit limitations / unresolved items

- The `ObservedAccountIdentity` supplied to this pure function must eventually be produced by a separately reviewed MT5 session adapter. This fixture does not prove that adapter or terminal identity.
- A worker must bind its MT5 session once and re-check identity before inventory reconciliation and before any future action; that lifecycle is not implemented here.
- Ticket/identifier and order/deal/position linkage semantics remain unresolved; no linking algorithm is defined.
- No durable state, lock, duplicate-submit recovery, broker response reconciliation, or order execution behavior is implemented.
- No multi-terminal topology or simultaneous-session behavior is established.
- No account is connected or activated; active V3.1 remains out of scope and unchanged.

## Validation command

Run from the multi-account worktree with the project venv:

```powershell
& 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe' -m unittest tests/test_sp2l_broker_object_ownership_contract_research.py -v
```

The test result must be recorded only after a local run. Expected count: 12 synthetic tests.
