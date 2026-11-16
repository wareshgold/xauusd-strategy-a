# MT5 Order–Deal–Position Linkage — Source Research (2026-11-16)

**Branch:** `research/multi-account-foundation-rfc-20261116`  
**Classification:** offline research only; non-canonical; no worker integration; no MT5 session or broker account accessed.

## Executive finding

Official MQL5 documentation defines explicit identifier relationships, but it also distinguishes a stable position identifier from a mutable/current position ticket. This is enough to reject a blanket equality assumption, but not enough to authorize a production reconciliation algorithm or broker-specific lifecycle semantics.

The most important documented distinction is:

- `POSITION_IDENTIFIER`: stable identifier for a position lifecycle.
- `POSITION_TICKET`: current position ticket; it usually matches the opening order ticket but may change due to server service operations. In netting reversal, the identifier remains while the ticket is replaced.
- `ORDER_POSITION_ID` and `DEAL_POSITION_ID`: position identifier fields, not documented as aliases for the current `POSITION_TICKET`.
- `DEAL_ORDER`: the order ticket on which that deal was executed.

Sources: [Position Properties](https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties), [Order Properties](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties), [Deal Properties](https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties).

## 1. Entity and field semantics confirmed by official MQL5 docs

| Entity / field | Officially documented meaning | Research interpretation |
|---|---|---|
| `ORDER_TICKET` | Unique order ticket | Order primary reference within its account and object-kind namespace |
| `ORDER_POSITION_ID` | Position identifier set on an order when executed; identifies the position opened or modified | Link to position lifecycle identifier; do not equate with current position ticket |
| `DEAL_TICKET` | Unique deal ticket | Deal primary reference within account and object-kind namespace |
| `DEAL_ORDER` | Order ticket on which the deal was executed | Explicit Deal → Order reference |
| `DEAL_POSITION_ID` | Identifier of the position affected by the deal; shared across deals during that position's lifetime | Link to position lifecycle identifier |
| `POSITION_IDENTIFIER` | Unique identifier that does not change during position lifecycle; corresponds to the opening order ticket; appears in related orders and deals | Stable lifecycle key supported by the documented fields |
| `POSITION_TICKET` | Ticket assigned to a position; usually matches opening order ticket but can change after server service operations | Current operational ticket, not stable lifecycle key |

The documented relationship supported by these fields is:

`DEAL_ORDER -> ORDER_TICKET`  
`ORDER_POSITION_ID -> POSITION_IDENTIFIER`  
`DEAL_POSITION_ID -> POSITION_IDENTIFIER`

This is a field-level relationship stated by MQL5. It is **not** a claim that every API wrapper exposes identical parameter naming, that every broker populates every field at every lifecycle stage, or that ticket equality is universal.

## 2. Position ticket versus position identifier

MQL5 explicitly states that `POSITION_TICKET` may change as a result of server service operations (example: swap charging with position re-opening). It also states that in netting reversal `POSITION_IDENTIFIER` does not change, while `POSITION_TICKET` is replaced by the ticket of the reversal order. Reversal is not provided in hedging mode.

Therefore:
- Never use `POSITION_TICKET == POSITION_IDENTIFIER` as a required invariant.
- Never use an old position ticket as the sole durable identity for the entire lifecycle.
- Preserve both fields separately when both are available.
- A position operation that requires a current ticket must use a freshly observed current ticket; durable history grouping must use the documented identifier field, subject to the API ambiguity below.

Source: [MQL5 Position Properties](https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties).

## 3. Netting and hedging

Official account properties define:
- `ACCOUNT_MARGIN_MODE_RETAIL_NETTING`: one position per symbol.
- `ACCOUNT_MARGIN_MODE_EXCHANGE`: netting-style position accounting.
- `ACCOUNT_MARGIN_MODE_RETAIL_HEDGING`: multiple individual positions may exist for one symbol.

MQL5's account-type guide confirms that netting can aggregate multiple deals into one symbol position, while hedging can retain multiple same-symbol positions, including opposite directions.

Research consequences:
- Symbol alone is not a position key in either mode.
- In netting, multiple deals can contribute to one position lifecycle; do not create a separate position identity per deal.
- In hedging, same-symbol positions must remain separate by their own position identifiers/current tickets.
- A future adapter must capture `ACCOUNT_MARGIN_MODE` as an explicit account capability and fail closed if unavailable or unsupported.
- Do not infer a broker's account mode from observed trade count.

Sources: [Account Properties](https://www.mql5.com/en/docs/constants/environment_state/accountinformation), [Account type: netting or hedging](https://www.mql5.com/en/book/automation/account/account_netting_hedge).

## 4. Partial fills and filling policy

Official order properties define `ORDER_STATE_PARTIAL`, `ORDER_VOLUME_INITIAL`, and `ORDER_VOLUME_CURRENT`. The reference describes the latter as initial/current volume and notes that order filling policy controls incomplete execution:

- FOK: execute only the specified volume or do not execute.
- IOC: execute available volume and cancel the remainder.
- RETURN: keep the remaining volume working after a partial fill; RETURN is not allowed for Market Execution.
- Pending orders use RETURN according to the MQL5 reference.

The MQL5 book's order-properties chapter adds a more specific description of how partial fills may appear in history: the historical order volume fields can describe the last filled part while other fills from the original requested volume appear as separate orders and deals. This is useful source evidence, but it must not be generalized into a broker-independent invariant without checking the actual terminal/API records and broker execution mode.

**No fixed cardinality rule is adopted here.** Do not assume one order always maps to exactly one deal, or that every partial fill has a single universal history representation.

Sources: [Order Properties](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties), [MQL5 book — Order properties](https://www.mql5.com/tr/book/automation/experts/experts_order_properties), [Execution modes and filling policies](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties).

## 5. Event ordering and reconciliation

The MQL5 transaction reference states that one trade request can generate several transactions and that their arrival priority is not guaranteed. It distinguishes order, history-order, deal, history-deal, position and request transaction types. For deal transactions, the structure may include deal ticket, order ticket, and the position ticket affected by that transaction. The transaction's `position` field is described as a position **ticket**, while `DEAL_POSITION_ID` is a position **identifier**.

Consequences:
- Do not equate `MqlTradeTransaction.position` with `DEAL_POSITION_ID` merely because both refer to a position.
- Event arrival order cannot be treated as a guaranteed lifecycle sequence.
- Reconciliation must be based on verified snapshots/history and explicit identifiers, not callback order or timestamps alone.
- Request acceptance is not proof that execution completed; inspect server return code and subsequent order/deal/position observations.

Sources: [MqlTradeTransaction](https://www.mql5.com/en/docs/constants/structures/mqltradetransaction), [OrderSend](https://www.mql5.com/en/docs/trading/ordersend).

## 6. History query semantics and a material Python API ambiguity

The MQL5 function `HistorySelectByPosition(position_id)` explicitly accepts a **position identifier** and selects orders/deals whose `ORDER_POSITION_ID` / `DEAL_POSITION_ID` match it.

However, the official Python Integration pages describe the `position=` argument of `history_orders_get()` and `history_deals_get()` using the phrase **position ticket**, while also saying it filters the `ORDER_POSITION_ID` and `DEAL_POSITION_ID` fields respectively. This naming is ambiguous against the MQL5 reference's explicit distinction between ticket and identifier.

Research gate:
- Do not pass a value from `POSITION_TICKET` to Python history `position=` based only on the parameter prose.
- Do not silently assume the Python wrapper parameter means `POSITION_IDENTIFIER` either.
- Verify the installed MetaTrader5 Python package behavior against official examples/source and deterministic captured records before choosing the adapter mapping.
- Until resolved, direct filtering over retrieved records by explicit `*_POSITION_ID` fields is conceptually clearer, but the retrieval scope/completeness still requires its own validation.

Sources: [HistorySelectByPosition](https://www.mql5.com/en/docs/trading/historyselectbyposition), [Python history_orders_get](https://www.mql5.com/en/docs/python_metatrader5/mt5historyordersget_py), [Python history_deals_get](https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py).

## 7. Close By

MQL5 defines `ORDER_POSITION_BY_ID` and `MqlTradeTransaction.position_by` for the opposite position used in a Close By operation. Deal entry can be `DEAL_ENTRY_OUT_BY`. This is a distinct opposite-position reference; it must not be collapsed into the primary `DEAL_POSITION_ID` edge.

Source: [Order Properties](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties), [Deal Properties](https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties), [MqlTradeTransaction](https://www.mql5.com/en/docs/constants/structures/mqltradetransaction).

## 8. Existing repository source boundary

The current research branch source audit previously found:
- V3.1 uses one process-level MT5 session.
- Existing lifecycle/history paths read explicit order/deal/position fields but were not built around a separately verified account identity plus durable account-scoped linkage graph.
- Existing startup inventory stores order and position ticket integers in separate sets.
- The broker-object ownership helper intentionally does not implement relationship resolution.

The new research in this document does not modify or integrate with those runner paths. No active V3.1 process, terminal, account, broker state, order, SL or TP was accessed.

## 9. Unresolved before a linkage adapter can be frozen

1. Exact Python binding semantics for `history_orders_get(position=...)` and `history_deals_get(position=...)` versus ticket/identifier terminology.
2. Actual broker/terminal representation of partial fills for the specific account type, symbol execution mode and filling policy.
3. Availability and stability of `POSITION_IDENTIFIER`, `ORDER_POSITION_ID`, and `DEAL_POSITION_ID` in the installed Python package version used by the Factory.
4. Whether a broker performs service operations that replace current position tickets, and the observable records around such changes.
5. Netting/hedging account mode for any future Fati account; this must be read from the account, not assumed.
6. Complete-history retrieval boundaries, pagination/time windows, and unavailable/partial query behavior.
7. Close By behavior if supported by the account/broker.

No algorithm is frozen for these unresolved cases.

## 10. Recommended next research gate

Build a mocked adapter fixture suite that preserves raw fields separately and tests:
- stable position identifier versus changed current ticket;
- multiple deals sharing one position identifier;
- netting reversal with unchanged identifier and changed ticket;
- same-symbol distinct hedging positions;
- partial-fill representations without imposing an unsupported one-order/one-deal cardinality;
- close-by opposite-position references;
- unavailable/partial history and event reordering;
- Python history-query parameter ambiguity.

Only after these fixtures are reviewed should a narrow, read-only adapter contract be proposed. No MT5 connection experiment is authorized by this document.
