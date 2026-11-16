# Account Identity Isolation Contract — Offline Research

**Status:** synthetic research fixture; non-canonical; not connected to MT5.

## Purpose

Establish the smallest fail-closed identity boundary before creating account workers. A worker must not proceed unless the broker, server, and opaque login reference observed at its adapter boundary exactly match the account's configured identity.

## Contract

- `account_key`: lowercase namespace-safe identifier (1–32 characters; letters, digits, underscore, hyphen; starts with a letter or digit).
- `broker`, `server`, `login_ref`: explicit non-empty strings.
- `login_ref` is an opaque operator-managed reference. Do not commit raw account login values, passwords, API keys, tokens, or other credentials.
- Identity mismatch raises `AccountIdentityMismatch`; the exception lists field names only and does not echo identity values.
- State namespace is deterministic and account-scoped: `accounts/<account_key>`.
- Candidate idempotency key is scoped beneath that account namespace. Identical candidate IDs on different accounts are intentionally distinct.
- This module does not create directories, read/write state, connect to a broker, submit orders, or manage positions.

## Synthetic validation

Run:

```powershell
python -m unittest tests.test_sp2l_account_isolation_contract_research -v
```

Fixtures use synthetic broker/server/login references only.

## Explicit limitations

This contract is not yet an MT5 identity adapter. The mechanism for deriving and protecting a stable `login_ref`, terminal/process ownership, and safe multi-terminal topology remains to be specified and verified. The contract alone does not prove account isolation at the broker boundary.
