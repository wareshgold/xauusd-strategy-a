# Paired Order/Deal History Observation — Research Contract (2026-11-16)

**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Classification:** offline research; non-canonical; no provider calls.  
**Status:** implementation and synthetic tests authored; local validation pending.

## Purpose

The read-only history adapter deliberately returns independent order and deal query outcomes. This small pure-Python layer pairs those outcomes under one supplied position lifecycle identifier so downstream research cannot accidentally treat one successful query as proof that both succeeded.

## Deterministic contract

- Require one `HistoryQueryResult` tagged `ORDERS` and one tagged `DEALS`.
- Require both observations to carry the same `position_identifier`.
- Preserve each result object and its raw records independently; do not merge, sort, filter, deduplicate, or reconcile rows.
- If both statuses are `EMPTY` or `NON_EMPTY`, classify the pair as `BOTH_RESPONSES_VALID`.
- If either status is `ERROR`, classify the pair as `AT_LEAST_ONE_QUERY_FAILED`.
- Reject swapped query kinds, wrong result types, and mismatched identifiers.

## Critical interpretation boundary

`BOTH_RESPONSES_VALID` means only that both injected query calls returned a recognized tuple-shaped outcome. Two empty tuples do **not** prove complete history, prove that a position never existed, or authorize recovery/bootstrap. A non-empty order result and empty deal result (or vice versa) remains an observation requiring separate source/fixture interpretation; this module does not explain the asymmetry.

The pair status is not a broker state, not an order/position linkage result, and not an execution decision. It must not be used alone to restore state, bootstrap an account, place an order, or generate a BUY/SELL decision.

## Tests

`tests.test_sp2l_history_pair_observation_research` covers:
1. two empty responses;
2. non-empty orders with empty deals;
3. empty orders with non-empty deals;
4. one failed order query;
5. one failed deal query;
6. both queries failing independently;
7. mismatched position identifiers;
8. swapped query kinds.

All tests are synthetic and offline. No MetaTrader5 import, terminal initialization, filesystem access, broker call, Runner integration, or real history query is part of this contract.
