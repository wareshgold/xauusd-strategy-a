# MT5 Order–Deal–Position Linkage — Synthetic Fixture Plan (2026-11-16)

**Status:** research fixtures only; non-canonical; no broker connection; no execution or reconciliation algorithm is approved.

These fixtures encode only source-confirmed field meanings. Ticket values are synthetic. They are not examples of actual broker records and must not be used to infer XAUUSD execution behavior.

## Fixture A — Explicit order/deal/position identifier edges

| Record | Synthetic fields |
|---|---|
| Position P1 | `POSITION_TICKET=7001`, `POSITION_IDENTIFIER=9001` |
| Historical Order O1 | `ORDER_TICKET=8001`, `ORDER_POSITION_ID=9001` |
| Deal D1 | `DEAL_TICKET=6001`, `DEAL_ORDER=8001`, `DEAL_POSITION_ID=9001` |

**Expected source-level assertions:**
- D1's `DEAL_ORDER` explicitly references O1's order ticket.
- O1's `ORDER_POSITION_ID` and D1's `DEAL_POSITION_ID` match P1's `POSITION_IDENTIFIER`.
- P1's current ticket (7001) is deliberately different from its identifier (9001); no mismatch error is valid solely because these values differ.

## Fixture B — Position ticket replacement / service operation

| Observation | Synthetic fields |
|---|---|
| Earlier position snapshot | `POSITION_TICKET=7001`, `POSITION_IDENTIFIER=9001` |
| Later position snapshot | `POSITION_TICKET=7002`, `POSITION_IDENTIFIER=9001` |
| Historical order/deal records | `ORDER_POSITION_ID=9001`, `DEAL_POSITION_ID=9001` |

**Expected source-level assertions:**
- The two observations refer to the same documented position lifecycle identifier.
- The current position ticket changed.
- A durable lifecycle key must not be replaced by the new ticket.
- Do not infer which service event caused the change unless its broker/terminal record is available.

## Fixture C — Netting accumulation and reversal

| Record | Synthetic fields |
|---|---|
| Position before reversal | `POSITION_TICKET=7001`, `POSITION_IDENTIFIER=9001` |
| Deal D2 | `DEAL_TICKET=6002`, `DEAL_POSITION_ID=9001`, `DEAL_ENTRY=INOUT` |
| Position after reversal | `POSITION_TICKET=8002`, `POSITION_IDENTIFIER=9001` |

**Expected source-level assertions:**
- In netting reversal, MQL5 documents that the position identifier remains unchanged and the position ticket is replaced by the reversal order ticket.
- `DEAL_ENTRY_INOUT` denotes reversal.
- Do not create a new lifecycle identifier merely because direction or current ticket changes.
- This fixture does not define volume arithmetic, realized P/L, or broker-specific reversal timing.

## Fixture D — Hedging: same symbol, distinct positions

| Position | Synthetic fields |
|---|---|
| P1 | `symbol=XAUUSD.ecn`, `POSITION_TICKET=7001`, `POSITION_IDENTIFIER=9001` |
| P2 | `symbol=XAUUSD.ecn`, `POSITION_TICKET=7002`, `POSITION_IDENTIFIER=9002` |

**Expected source-level assertions:**
- Same symbol does not collapse P1 and P2.
- Each position lifecycle remains distinct by its own identifier.
- Opposite directions can coexist in hedging mode.
- No aggregation by symbol is allowed for ownership identity.

## Fixture E — Multiple deals associated with one position lifecycle

| Record | Synthetic fields |
|---|---|
| Position P1 | `POSITION_IDENTIFIER=9001` |
| Deal D1 | `DEAL_TICKET=6001`, `DEAL_POSITION_ID=9001`, `DEAL_ENTRY=IN` |
| Deal D2 | `DEAL_TICKET=6002`, `DEAL_POSITION_ID=9001`, `DEAL_ENTRY=IN` |
| Deal D3 | `DEAL_TICKET=6003`, `DEAL_POSITION_ID=9001`, `DEAL_ENTRY=OUT` |

**Expected source-level assertions:**
- Multiple deals may share one documented position identifier across its lifecycle.
- Deal tickets remain distinct.
- Do not assume one position equals one deal.
- Do not infer strategy ownership from position identifier alone; account, symbol, magic and source provenance remain separate checks.

## Fixture F — Partial execution: deliberately non-prescriptive alternatives

Two synthetic histories are retained as separate possibilities pending broker/API verification.

**F1 — Remaining order continues (RETURN-style behavior):**
- Initial request volume is 1.00.
- A deal records 0.40.
- The active order may remain with current volume 0.60 and partial state.
- Later execution/cancellation must be established from later order/deal observations.

**F2 — Available volume executes and remainder is canceled (IOC-style behavior):**
- Initial request volume is 1.00.
- A deal records 0.40.
- Remaining 0.60 is canceled under the IOC policy.

**F3 — FOK:**
- Full requested volume executes, or the order is not executed under the documented FOK policy.

**Expected source-level assertions:**
- Filling policy is an explicit input to interpretation.
- `ORDER_STATE_PARTIAL`, `ORDER_VOLUME_INITIAL`, `ORDER_VOLUME_CURRENT`, deal volumes and final order state must be retained independently.
- Do not sum or deduplicate deals using assumptions about one order/one deal.
- Do not infer the final state from a single transaction callback.

The MQL5 book also describes partial fills in history as potentially represented by separate orders/deals for individual fills. This is recorded as a source note, not promoted to a universal invariant until actual package/broker records are checked.

## Fixture G — Close By uses an opposite-position reference

| Record | Synthetic fields |
|---|---|
| Close-by order O3 | `ORDER_TICKET=8003`, `ORDER_POSITION_ID=9001`, `ORDER_POSITION_BY_ID=9002` |
| Close-by deal D4 | `DEAL_TICKET=6004`, `DEAL_POSITION_ID=9001`, `DEAL_ENTRY=OUT_BY` |

**Expected source-level assertions:**
- Primary position identifier and opposite-position identifier are distinct edges.
- `ORDER_POSITION_BY_ID` / transaction `position_by` must not be silently treated as the same edge as `ORDER_POSITION_ID`.
- This fixture does not assert all broker-specific Close By history fields.

## Fixture H — Event reordering and request lifecycle

A single request may produce multiple trade transactions; MQL5 documentation says arrival priority is not guaranteed.

Synthetic delivery order:
1. DEAL_ADD
2. HISTORY_ORDER_ADD
3. ORDER_DELETE
4. REQUEST response

**Expected source-level assertions:**
- The consumer cannot require a single fixed callback order.
- Duplicate or delayed observations must be retained/deduplicated by explicit object identity, not arrival sequence alone.
- A request result is not itself proof that a position snapshot is complete.

## Fixture I — Python history-query naming ambiguity

The MQL5 function `HistorySelectByPosition(position_id)` explicitly accepts `POSITION_IDENTIFIER`. The Python pages describe `history_orders_get(position=...)` and `history_deals_get(position=...)` as taking a “position ticket”, while saying they filter `ORDER_POSITION_ID` and `DEAL_POSITION_ID`.

**Expected source-level assertions:**
- Preserve `POSITION_TICKET` and `POSITION_IDENTIFIER` as distinct raw fields.
- Do not create a Python adapter mapping from the parameter prose alone.
- Add a dedicated package-level mocked/recorded compatibility test only after the installed Python binding behavior is independently established.
- Until then, mark history lookup by `position=` as unresolved.

## Fixture J — Unavailable or incomplete history

| Observation | Expected handling |
|---|---|
| History query returns no records and reports success | Valid empty result only for the exact requested range/scope; does not prove lifetime history completeness |
| Python history query returns `None` | Query failure; not equivalent to empty history |
| Current positions query unavailable | Inventory unavailable; halt ownership/recovery classification |
| History window begins after lifecycle start | Partial history; do not claim full lifecycle reconciliation |
| One of orders/deals history queries fails | Incomplete linkage evidence; do not silently reconcile from the remaining side |

Python Integration documentation states history retrieval functions return `None` on error and expose `last_error()`. The adapter must preserve that distinction.

## Fixture review status

The original A–J fixture plan is now represented by a narrow pure-Python fact model and 11 synthetic tests:
- Model: `scripts/sp2l_order_deal_position_linkage_facts_research.py`
- Tests: `tests/test_sp2l_order_deal_position_linkage_facts_research.py`
- Test cases cover explicit order/deal references, position ticket versus identifier, ticket replacement, netting reversal, same-symbol hedging positions, multiple deals per lifecycle, Close By's opposite reference, and preservation of raw partial-fill fields.

**Execution status:** tests are authored but have not yet been run in the operator's local environment. No test-pass claim is made. The model does not query history, reconcile broker objects, infer ticket aliases, or decide partial-fill semantics. Python history-query parameter meaning, broker-specific partial-fill representation, callback ordering, and durable reconciliation remain unresolved.



## Fixture K — Python history `position=` filter key (documentation-derived)

This fixture models the documented field filter only. It does not call or emulate the compiled MetaTrader5 Python extension.

| Observed fact | Synthetic value |
|---|---:|
| Current `POSITION_TICKET` | 7001 |
| Stable `POSITION_IDENTIFIER` | 9001 |
| Order `ORDER_POSITION_ID` | 9001 |
| Deal `DEAL_POSITION_ID` | 9001 |

**Expected assertions:**
- The documented orders-history filter matches the supplied value against `ORDER_POSITION_ID`.
- The documented deals-history filter matches the supplied value against `DEAL_POSITION_ID`.
- With deliberately different values (7001 vs 9001), the documented field match is 9001, not the current position ticket 7001.
- A different identifier (for example 9002) does not match either record.
- These are source-derived predicate tests, not package-version compatibility tests and not broker evidence.

Source basis: official Python Integration pages for `history_orders_get` and `history_deals_get`, official Position Properties, `HistorySelectByPosition`, and MQL5 book section 7.9.15. See `docs/research/SP2L_PYTHON_HISTORY_POSITION_FILTER_SOURCE_RESOLUTION_2026-11-16.md`.
