# Multi-Account Recovery and Delivery Fixtures (Research Only)

**Date:** 2026-11-16  
**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Status:** synthetic contract; non-canonical; no MT5 or filesystem access.

## Purpose

Add explicit offline classifications for state integrity, recovery readiness, account-scoped event identity, and duplicate candidate delivery. The module consumes supplied facts only. It does not read files, inspect MT5, persist events, or send orders.

## Frozen research contract

### State classification

A supplied snapshot is classified as exactly one of:

- `MISSING`: no state file was reported.
- `VALID`: parsing succeeded, payload is a mapping, and schema version matches.
- `CORRUPT`: parsing failed or payload is not a mapping.
- `INCOMPATIBLE`: payload parsed as a mapping but schema version differs.

This is intentionally not the V3.1 loader behavior. It is a new research contract and does not alter the active Runner.

### Recovery disposition

Recovery halts if account identity is unverified, broker inventory is unavailable, the event journal is incomplete, or order/position linkage is marked ambiguous.

- Valid state plus complete, verified observations → `RESTORE`.
- Missing state plus complete journal and verified empty broker inventory → `BOOTSTRAP_EMPTY`.
- Missing state with non-empty inventory, corrupt state, or incompatible state → `HALT`.

The boolean `linkage_ambiguous` is an explicit fixture input. This contract does not invent how pending orders become positions, how fills are identified, or how broker tickets should be linked.

### Account event and candidate isolation

- Event IDs are namespaced as `accounts/<account_key>/event/<event_id>`.
- Candidate delivery is deduplicated only against keys in the same account namespace.
- The same candidate ID may be NEW for one account even if another account has already processed it.
- These helpers classify keys only; they do not define durable storage, delivery guarantees, or transactional exactly-once execution.

## Synthetic fixture coverage

1. Missing, valid, corrupt, and schema-incompatible state.
2. Missing state with empty versus non-empty inventory.
3. Unverified identity, unavailable inventory, incomplete event journal, and ambiguous linkage.
4. Event namespace separation across accounts.
5. Duplicate candidate delivery within an account and independent delivery across accounts.

## Explicit limitations

- No MT5 import, initialization, terminal launch, account connection, inventory query, or broker action.
- No file read/write, state migration, event replay, lock acquisition, or Telegram operation.
- No definition of execution/fill semantics or order-to-position linkage.
- No reuse of the unresolved Fati RR1/BE+5 policy.
- No modification of the active V3.1 Runner, its runtime state, event stream, or trailing behavior.
- No canonical SP2L geometry or production signal decision.

## Validation

The test module is intended to run locally in the dedicated research worktree with:

```powershell
python -m unittest tests.test_sp2l_multi_account_recovery_contract_research -v
```

Until the operator reports the local result, these tests must be described as authored, not passed.
