# Read-Only Mocked History Adapter — Research Contract (2026-11-16)

**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Classification:** offline research; non-canonical; injected fake provider only.  
**Status:** implementation and synthetic tests authored; operator-local validation pending.

## 1. Purpose

Define a narrow, deterministic seam for exercising the documented Python history-query call shape without importing MetaTrader5, initializing a terminal, connecting to a broker, or touching the active V3.1 Runner.

The adapter accepts an injected provider. The intended test provider is a local fake with deterministic return values. Passing a real MT5 module/provider is explicitly outside this research contract and requires a separately authorized compatibility experiment.

## 2. Source-aligned query key

The two supported calls pass the supplied position lifecycle identifier as the keyword argument `position`:

- orders: `history_orders_get(position=POSITION_IDENTIFIER)`
- deals: `history_deals_get(position=POSITION_IDENTIFIER)`

This is based on the documentation-level source resolution in `SP2L_PYTHON_HISTORY_POSITION_FILTER_SOURCE_RESOLUTION_2026-11-16.md`. It is not runtime verification of the installed MetaTrader5 Python package.

The adapter does not accept a current `POSITION_TICKET` parameter and does not derive an identifier from a ticket.

## 3. Query result classification

| Provider return | Adapter status | Meaning in this contract |
|---|---|---|
| Non-empty tuple | `NON_EMPTY` | Query returned records; records are preserved as opaque objects |
| Empty tuple | `EMPTY` | Valid empty result; not an error |
| `None` | `ERROR` | API-style failure sentinel; capture opaque `last_error()` payload |
| Exception | `ERROR` | Provider exception; record exception type, do not invent broker meaning |
| Non-tuple value | `ERROR` | Unexpected result shape; do not silently coerce |

The documented Python API returns tuples of records (or `None` on error). The fake tests model this shape. The adapter intentionally does not parse namedtuple fields, rewrite rows, filter the returned payload again, or infer whether the history is complete.

## 4. Preservation and non-goals

- The query kind and supplied `position_identifier` are explicit in every result.
- Returned records are preserved as an immutable tuple container; each row remains opaque and unchanged.
- The provider's `last_error()` payload is preserved opaquely. The adapter does not decode error codes or messages.
- Invalid identifier types and non-positive values are rejected before the provider is called.
- Orders and deals are separate calls and separate outcomes; success of one does not imply success of the other.
- A valid empty result is not proof of a complete history window.
- No time-window completeness is inferred; no completeness metadata is synthesized.
- No order/deal/position reconciliation, deduplication, fill interpretation, ownership inference, P/L calculation, or execution decision is performed.
- No assumptions are made about one order to one deal cardinality, partial fills, hedging/netting reconciliation, transaction arrival order, or broker-specific history behavior.

## 5. Failure boundaries

The result object distinguishes:
- `API_RETURNED_NONE`
- `PROVIDER_EXCEPTION`
- `INVALID_RESULT_TYPE`

If `last_error()` itself raises, only its exception class name is retained as diagnostic metadata; it is not represented as a broker error payload. Exception messages are not copied into the result.

## 6. Synthetic validation plan

Tests use a local fake provider and cover:
1. exact `position_identifier` argument passed to the order query;
2. exact `position_identifier` argument passed to the deal query;
3. valid empty tuple;
4. non-empty tuple preservation;
5. `None` distinguished from empty for both query kinds;
6. provider exception classification;
7. `last_error()` failure classification;
8. unexpected result type rejection;
9. independent order/deal calls;
10. invalid identifiers rejected before provider invocation;
11. no row filtering or reconciliation by the adapter;
12. immutable tuple container and explicit query kind.

Test module: `tests.test_sp2l_read_only_history_adapter_research`.

## 7. Validation boundary and next gate

After the operator runs the focused test module locally, a passing result will validate only this pure-Python injected-provider contract against synthetic fixtures. It will not validate the installed package, terminal, broker, history completeness, account mode, or any execution behavior.

A later independent test may compare a controlled recorded API response with explicit field-level filtering, but it requires explicit operator authorization and must not attach to or interfere with the active Runner. No such test is included here.
