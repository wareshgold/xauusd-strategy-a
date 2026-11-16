# SP2L History Completeness Evidence Protocol — Research Draft (2026-11-16)

**Status:** research draft; not canonical; no production caller authorized  
**Scope:** define what can and cannot be evidenced from documented MT5 Python history APIs  
**Safety:** documentation/source analysis only; no MT5 import, terminal initialization, broker query, or Runner access

## 1. Research question

What evidence is sufficient to let a recovery caller assert that the historical orders and deals relevant to an account/position have been completely observed?

The current History-to-Recovery Gate requires an independently supplied `history_completeness_verified=True`. This document does not turn that flag into an automatic pass. It specifies the documented observations available and the limits of what they establish.

## 2. Source-confirmed API behavior

Official MetaTrader 5 Python Integration documentation states:

- `history_orders_get(date_from, date_to, ...)` returns orders in the specified time interval; it returns a named-tuple collection, or `None` on error. The documentation also provides a position-filtered form.
- `history_deals_get(date_from, date_to, ...)` returns deals in the specified time interval; it returns a named-tuple collection, or `None` on error. The documentation also provides position- and order-filtered forms.
- `history_orders_total(date_from, date_to)` reports the number of historical orders in the interval.
- `history_deals_total(date_from, date_to)` reports the number of historical deals in the interval.
- MQL5 `HistorySelect(from_date, to_date)` selects the history of orders and deals for a specified period of **server time**.

Sources:
- Python `history_orders_get`: https://www.mql5.com/en/docs/python_metatrader5/mt5historyordersget_py
- Python `history_deals_get`: https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py
- Python `history_orders_total`: https://www.mql5.com/en/docs/python_metatrader5/mt5historyorderstotal_py
- Python `history_deals_total`: https://www.mql5.com/en/docs/python_metatrader5/mt5historydealstotal_py
- MQL5 `HistorySelect`: https://www.mql5.com/en/docs/trading/historyselect
- MQL5 Python history chapter: https://www.mql5.com/en/book/advanced/python/python_history_deals

These sources describe API behavior. They do not promise that the terminal has downloaded or retained every record that exists in a broker's backend archive, nor do they define a broker-independent completeness attestation.

## 3. Evidence scope must be explicit

Any future evidence record must identify, without credentials:

- verified account identity reference (the existing account-isolation contract, not a display name alone);
- terminal/session identity reference and observed server name;
- exact `date_from` and `date_to` values passed to the APIs;
- declared time basis and its source; do not silently convert local time to server time or infer an offset;
- separate ORDERS and DEALS observations;
- API/package version and terminal build as observed metadata, not as proof of completeness;
- observation timestamp and a stable evidence-manifest/hash reference.

An unspecified interval, ambiguous time basis, unverified account identity, or missing query kind makes the evidence unusable for recovery.

## 4. Deterministic consistency checks that may be implemented

For one fixed account and one explicit interval, collect independently:

1. `history_orders_total(date_from, date_to)`;
2. `history_orders_get(date_from, date_to)`;
3. `history_deals_total(date_from, date_to)`;
4. `history_deals_get(date_from, date_to)`.

Preserve raw responses and errors. Do not silently retry, filter, merge, deduplicate, or repair rows in this evidence layer.

For each query kind, classify:
- API error / exception / invalid result;
- valid collection;
- reported total;
- returned row count;
- count agreement or disagreement.

A `None` result from either `*_get` is an error, not an empty history. A valid empty collection is distinct from an error. A mismatch between `*_total` and the corresponding returned collection count is an inconsistency and must fail closed.

The four calls are separate API observations. The documentation does not guarantee they are an atomic snapshot. Therefore count agreement is only an API-level consistency check for the observed interval, not proof that no broker-side record is missing.

## 5. What these checks do NOT prove

Even when both totals equal their corresponding collection lengths:

- the broker's backend archive contains no additional records;
- the terminal has downloaded all records available from the broker;
- the selected interval includes the full lifecycle of every relevant position;
- records outside the interval cannot affect recovery;
- a second query is guaranteed to observe the same snapshot;
- history is immutable while the calls are being made;
- position-filtered results are globally complete;
- order/deal rows can be reconciled one-to-one;
- partial fills, reversals, Close By, or service operations have a particular representation;
- the installed MetaTrader5 Python package behaves identically to the documentation.

Repeated identical results may establish observed stability across those observations only. They do not independently establish broker archive completeness.

## 6. Proposed evidence dispositions (not yet implemented)

Use descriptive, non-authorizing outcomes:

- `INVALID_SCOPE`: missing or ambiguous account/time-range provenance.
- `QUERY_FAILED`: any required API call failed or returned an invalid shape.
- `COUNT_MISMATCH`: total and returned row count disagree for either query kind.
- `OBSERVED_CONSISTENT_FOR_SCOPE`: all four calls succeeded and both count comparisons agree.
- `COMPLETENESS_UNPROVEN`: default interpretation for all API-only evidence until an independent, source-backed completeness mechanism is identified.

None of these outcomes, including `OBSERVED_CONSISTENT_FOR_SCOPE`, is by itself permission to bootstrap or restore production state. The existing recovery gate must continue to fail closed unless a separately approved completeness contract exists.

## 7. Open source questions before any completeness claim

1. Is there an official MetaQuotes guarantee or terminal API that attests the account history is fully synchronized with the broker archive?
2. What exact server-time interpretation does the installed Python package apply to naive and timezone-aware `datetime` inputs?
3. Does the installed package expose any reliable history synchronization status, and what does that status guarantee?
4. Can a broker provide an independently verifiable export or statement covering the required interval, and how would its scope be reconciled without inventing linkage semantics?
5. What operational rule defines the start/end of the history scope for an open position whose lifecycle predates the local journal?

Until these questions are resolved, absolute history completeness remains **unresolved**.

## 8. Implementation boundary

A future pure-Python evidence model may validate scope metadata, preserve four independent API observations, distinguish `None` from empty collections, and detect count mismatches using synthetic fixtures. It must not set `history_completeness_verified=True` merely because those checks pass.

No MT5 runtime experiment is authorized by this document. No production recovery integration, account activation, order operation, or active V3.1 Runner modification is included.
